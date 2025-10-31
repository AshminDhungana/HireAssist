import os
import uuid
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.main import app
from app.core.database import async_session
from app.core.security import get_password_hash, create_access_token
from app.models.users import User
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.core.config import settings


@pytest.mark.skipif(os.getenv("RUN_INTEGRATION_TESTS") != "1", reason="Integration tests are disabled by default. Set RUN_INTEGRATION_TESTS=1 to enable")
@pytest.mark.asyncio
async def test_upload_and_parse_flow_integration():
    """
    Integration test for upload -> parse flow.

    Requires a running PostgreSQL test database and proper env vars (DATABASE_URL, SECRET_KEY).
    This test will:
      - create a user and candidate in the real DB
      - upload a small PDF via the /upload endpoint
      - call the parse endpoint
      - verify parsed_data was saved to the resume record

    NOTE: This test mutates the real DB; run in an isolated test DB.
    """

    # Create user and candidate in DB
    test_email = f"integ-{uuid.uuid4().hex[:8]}@example.com"
    async with async_session() as session:
        user = User(email=test_email, password_hash=get_password_hash("password"))
        session.add(user)
        await session.commit()
        await session.refresh(user)

        candidate = Candidate(user_id=user.id, name="Integration Candidate", email=test_email)
        session.add(candidate)
        await session.commit()
        await session.refresh(candidate)

    # Create token for the created user
    token = create_access_token(str(user.id))

    client = TestClient(app)

    # Create a small text file saved as .pdf to exercise upload path
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', mode='wb') as tf:
        tf.write(b"Integration test PDF content\nJohn Doe\nSkills: Python, SQL")
        tmp_filepath = tf.name

    try:
        # Upload file
        with open(tmp_filepath, 'rb') as f:
            files = {"file": ("integ.pdf", f, "application/pdf")}
            headers = {"Authorization": f"Bearer {token}"}
            resp = client.post("/api/v1/resumes/upload", files=files, headers=headers)
            assert resp.status_code == 201, resp.text
            data = resp.json()
            resume_id = data.get("resume_id")
            assert resume_id

        # Call parse endpoint
        resp2 = client.post(f"/api/v1/{resume_id}/parse", headers=headers, json={"use_rag": False, "extract_detailed": False})
        assert resp2.status_code == 200, resp2.text

        # Verify resume record now has parsed_data in DB
        async with async_session() as session:
            stmt = select(Resume).where(Resume.id == uuid.UUID(resume_id))
            result = await session.execute(stmt)
            resume_obj = result.scalars().first()
            assert resume_obj is not None
            assert resume_obj.parsed_data is not None
            # basic sanity checks
            assert isinstance(resume_obj.parsed_data, dict)
            assert "raw_text" in resume_obj.parsed_data

    finally:
        # Cleanup created DB records (resume, candidate, user) and temp file
        async with async_session() as session:
            # delete resume if exists
            try:
                stmt = select(Resume).where(Resume.id == uuid.UUID(resume_id))
                res = await session.execute(stmt)
                r = res.scalars().first()
                if r:
                    await session.delete(r)
                    await session.commit()
            except Exception:
                pass

            try:
                stmt = select(Candidate).where(Candidate.user_id == user.id)
                res = await session.execute(stmt)
                c = res.scalars().first()
                if c:
                    await session.delete(c)
                    await session.commit()
            except Exception:
                pass

            try:
                stmt = select(User).where(User.id == user.id)
                res = await session.execute(stmt)
                u = res.scalars().first()
                if u:
                    await session.delete(u)
                    await session.commit()
            except Exception:
                pass

        try:
            os.unlink(tmp_filepath)
        except Exception:
            pass
