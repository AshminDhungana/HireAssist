from unittest.mock import MagicMock, AsyncMock
import pytest
from app.main import app
from app.core.database import get_db


@pytest.fixture
def async_db_session():
    """Create a MagicMock-based async DB session with awaitable commit/refresh/rollback."""
    session = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()
    # default execute is an AsyncMock; tests can assign return_value as needed
    session.execute = AsyncMock()
    return session


@pytest.fixture
def db_session(async_db_session):
    """Override the FastAPI `get_db` dependency to yield our async MagicMock session.

    Tests that accept the `db_session` fixture will get the mocked session and the
    app dependency will be overridden for the duration of the test.
    """

    async def _fake_get_db():
        yield async_db_session

    app.dependency_overrides[get_db] = _fake_get_db
    try:
        yield async_db_session
    finally:
        # cleanup override after test
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def make_mock_result():
    """Factory to create a DB execute result that implements scalars().first()."""

    def _make(value):
        result = MagicMock()
        result.scalars.return_value.first.return_value = value
        return result

    return _make
import os
import shutil
import pytest
from app.services.resumeparser import ResumeParser
import uuid

@pytest.fixture
def test_data_dir():
    """Create and return a temporary test data directory"""
    test_dir = os.path.join(os.path.dirname(__file__), "test_data")
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir
    shutil.rmtree(test_dir)

@pytest.fixture
def sample_pdf(test_data_dir):
    """Create a sample PDF file for testing"""
    pdf_path = os.path.join(test_data_dir, "test_resume.pdf")
    # Create minimal PDF for testing
    with open(pdf_path, "w", encoding="utf-8") as f:
        f.write("John Doe\n")
        f.write("john@example.com\n")
        f.write("123-456-7890\n")
        f.write("\nExperience:\n")
        f.write("Software Engineer at Tech Corp (2020-2023)\n")
        f.write("Led backend development team\n")
        f.write("\nEducation:\n")
        f.write("B.S. Computer Science, University of Technology (2016-2020)\n")
        f.write("\nSkills:\n")
        f.write("Python, FastAPI, Docker\n")
    return pdf_path

@pytest.fixture
def encrypted_pdf(test_data_dir):
    """Create an encrypted PDF file for testing"""
    pdf_path = os.path.join(test_data_dir, "encrypted.pdf")
    with open(pdf_path, "wb") as f:
        # Write minimal PDF with encryption flag
        f.write(b"%PDF-1.7\n%\xE2\xE3\xCF\xD3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R/Encrypt 3 0 R>>\nendobj\n")
    return pdf_path

@pytest.fixture
def test_user_token():
    """Create a test user token"""
    from app.core.security import create_access_token
    return create_access_token(str(uuid.uuid4()))

@pytest.fixture
def test_resume_id():
    """Return a test resume ID"""
    return str(uuid.uuid4())

@pytest.fixture
def test_resume_data(test_resume_id):
    """Return a test resume record"""
    return {
        "id": test_resume_id,
        "filename": "test_resume.pdf",
        "candidate_id": str(uuid.uuid4()),
        "file_path": "test_resume.pdf",
        "parsed_data": None,
        "raw_text": None,
        "skills": [],
        "experience_years": None,
        "education_level": None
    }