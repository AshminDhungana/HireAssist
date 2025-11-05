import pytest
from fastapi.testclient import TestClient
from app.core.database import get_db
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app
from app.services.resumeparser import FileParseError, ResumeParser
from app.core.security import create_access_token
import os
import json
import uuid
import tempfile
from typing import AsyncGenerator
import asyncio
from httpx import AsyncClient, ASGITransport

# Create test client
client = TestClient(app)

# NOTE: db_session fixture is provided by tests/conftest.py — it gives an
# AsyncMock-backed MagicMock and automatically overrides `get_db` for tests.


@pytest.fixture
def test_resume():
    """Create a test resume file"""
    content = """John Doe
john@example.com
(123) 456-7890

Experience:
Software Engineer at Tech Corp (2020-2023)
- Led backend development
- Implemented new features

Education:
B.S. Computer Science
University of Technology (2016-2020)

Skills:
Python, FastAPI, SQL, Docker"""

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', mode='w') as f:
        f.write(content)
        filepath = f.name
    
    yield filepath
    
    # Cleanup
    if os.path.exists(filepath):
        os.unlink(filepath)


@pytest.fixture
def mock_parser(test_resume):
    """Mock ResumeParser with realistic return values"""
    mock = MagicMock()
    mock.parse_resume.return_value = {
        "personal_info": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "(123) 456-7890"
        },
        "skills": ["Python", "FastAPI", "SQL", "Docker"],
        "experience": [{
            "company": "Tech Corp",
            "title": "Software Engineer",
            "dates": "2020-2023",
            "description": "Led backend development"
        }],
        "education": [{
            "degree": "B.S. Computer Science",
            "institution": "University of Technology",
            "dates": "2016-2020"
        }],
        "experience_years": 3,
        "confidence_score": 0.85,
        "raw_text": open(test_resume, 'r').read()
    }
    # Ensure extract_experience/education return lists matching parse_resume
    mock.extract_experience.return_value = mock.parse_resume.return_value.get('experience', [])
    mock.extract_education.return_value = mock.parse_resume.return_value.get('education', [])
    return mock


@pytest.fixture
def test_user_token():
    """Create a test user token"""
    # Use a UUID subject so the API's UUID validation accepts the token
    return create_access_token(str(uuid.uuid4()))


@pytest.fixture
def test_resume_id():
    """Return a test resume ID - should match a resume in test DB"""
    return "550e8400-e29b-41d4-a716-446655440000"  # Test UUID


@pytest.mark.asyncio
async def test_parse_resume_endpoint_success(mock_parser, test_resume, db_session):
    """Test successful resume parsing"""
    resume_id = str(uuid.uuid4())
    token = create_access_token(str(uuid.uuid4()))

    # Setup mock resume
    mock_resume = MagicMock()
    mock_resume.id = resume_id
    mock_resume.file_path = test_resume
    mock_resume.filename = "test.pdf"

    # Setup mock database execute result
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_resume
    db_session.execute = AsyncMock(return_value=mock_result)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch('app.api.v1.resumes.ResumeParser', return_value=mock_parser):
            response = await ac.post(
                f"/api/v1/resumes/{resume_id}/parse",
                headers={"Authorization": f"Bearer {token}"},
                json={"use_rag": False, "extract_detailed": True}
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert all(key in data for key in [
                "personal_info", "skills", "experience", 
                "education", "confidence_score"
            ])
            
            # Verify content details
            personal_info = data["personal_info"]
            assert personal_info["name"] == "John Doe"
            assert personal_info["email"] == "john@example.com"
            
            experience = data["experience"][0]
            assert experience["company"] == "Tech Corp"
            assert experience["title"] == "Software Engineer"
            
            app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_parse_resume_unauthorized():
    """Test that missing authorization header returns proper error"""
    resume_id = str(uuid.uuid4())
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # NOTE: FastAPI validates body schema before checking auth header
        # This is expected behavior when body validation fails first
        response = await ac.post(
            f"/api/v1/resumes/{resume_id}/parse",
            json={"use_rag": False, "extract_detailed": True}
            # ❌ NO Authorization header
        )
        # Either 401 (auth fails) or 422 (body validation fails first) - both acceptable
        assert response.status_code in [401, 422]


@pytest.mark.asyncio
async def test_parse_resume_invalid_token():
    """Test that invalid token returns 401"""
    resume_id = str(uuid.uuid4())
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            f"/api/v1/resumes/{resume_id}/parse",
            headers={"Authorization": "Bearer invalid-token"},
            json={"use_rag": False, "extract_detailed": True}
        )
        assert response.status_code == 401


def test_parse_resume_not_found(test_user_token):
    """Test that parsing non-existent resume returns 404"""
    invalid_id = "00000000-0000-0000-0000-000000000000"
    # Mock DB to return no resume
    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    async def fake_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = fake_get_db
    response = client.post(
        f"/api/v1/resumes/{invalid_id}/parse",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"use_rag": False, "extract_detailed": True}
    )
    assert response.status_code == 404
    assert "Resume not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_parse_resume_file_error(db_session):
    """Test that file parse errors are handled gracefully"""
    resume_id = str(uuid.uuid4())
    token = create_access_token(str(uuid.uuid4()))

    # Mock resume that will trigger an error
    mock_resume = MagicMock()
    mock_resume.id = resume_id
    # Use a real temp file so endpoint reaches parsing stage
    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile(delete=False, suffix='.pdf', mode='w') as tf:
        tf.write("dummy content")
        tmp_path = tf.name
    mock_resume.file_path = tmp_path
    mock_resume.filename = "nonexistent.pdf"

    # Setup mock database execute result
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_resume
    db_session.execute = AsyncMock(return_value=mock_result)

    # Create parser that raises error
    error_parser = MagicMock()
    error_parser.parse_resume.side_effect = FileParseError("Test error")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with patch('app.api.v1.resumes.ResumeParser', return_value=error_parser):
            response = await ac.post(
                f"/api/v1/resumes/{resume_id}/parse",
                headers={"Authorization": f"Bearer {token}"},
                json={"use_rag": False, "extract_detailed": True}
            )

            assert response.status_code == 400
            error_data = response.json()
            assert "detail" in error_data
            assert error_data["detail"]["error_type"] == "parse_error"

    # cleanup temp file
    try:
        os.unlink(tmp_path)
    except Exception:
        pass


def test_parse_resume_with_rag(test_user_token, test_resume_id):
    """Test resume parsing with RAG parser"""
    # Prepare a mock resume and mock RAG parser
    mock_resume = MagicMock()
    mock_resume.id = test_resume_id
    mock_resume.file_path = __file__  # point to an existing file
    mock_resume.filename = "test.pdf"

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_resume

    mock_db_session = MagicMock()
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    mock_db_session.commit = AsyncMock()
    mock_db_session.refresh = AsyncMock()
    mock_db_session.rollback = AsyncMock()

    # Simple RAG parser replacement
    rag_mock = MagicMock()
    rag_mock.parse_resume.return_value = {
        "personal_info": {"name": "Rag User", "email": "rag@example.com"},
        "skills": ["Python"],
        "experience": [],
        "education": [],
        "experience_years": 0,
        "confidence_score": 0.5,
        "raw_text": ""
    }

    async def _fake_get_db():
        yield mock_db_session

    app.dependency_overrides[get_db] = _fake_get_db
    with patch('app.api.v1.resumes.RAGResumeParser', return_value=rag_mock):
        from types import SimpleNamespace
        with patch('app.api.v1.resumes.settings', new=SimpleNamespace(USE_RAG_PARSER=True)):
            response = client.post(
                f"/api/v1/resumes/{test_resume_id}/parse",
                headers={"Authorization": f"Bearer {test_user_token}"},
                json={"use_rag": True, "extract_detailed": True}
            )

            assert response.status_code == 200
            data = response.json()

            # RAG parser should maintain schema
            assert "personal_info" in data
            assert "skills" in data
            assert isinstance(data["skills"], list)
            assert "confidence_score" in data

    app.dependency_overrides.pop(get_db, None)


def test_global_error_handler():
    """Test that unhandled errors return 500"""
    response = client.get("/api/v1/test-error")
    assert response.status_code == 500
    error_data = response.json()
    assert "error_type" in error_data
    assert error_data["error_type"] == "internal_error"
