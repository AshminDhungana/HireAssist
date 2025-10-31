import os
import json

from app.services.resumeparser import ResumeParser


def test_rule_based_parser_happy_path():
    """Test resume parser with sample resume from test_data directory."""
    # Use test data directory
    test_dir = os.path.join(os.path.dirname(__file__), "test_data")
    test_file = os.path.join(test_dir, "sample_resume.pdf")
    
    assert os.path.exists(test_file), f"sample_resume.pdf missing at {test_file}"

    parser = ResumeParser()
    parsed = parser.parse_resume(test_file, "application/pdf")

    # Basic sanity checks
    assert isinstance(parsed, dict)
    
    # personal_info may be present
    personal = parsed.get("personal_info", {})
    assert isinstance(personal, dict)

    # Expect an email and phone (from the sample resume)
    email = personal.get("email")
    phone = personal.get("phone")
    assert email is not None, f"expected email in parsed output, got: {personal}"
    assert phone is not None, f"expected phone in parsed output, got: {personal}"

    # Check skills
    skills = parsed.get("skills")
    assert isinstance(skills, list), f"skills should be a list, got: {type(skills)}"
    assert len(skills) >= 1, f"expected at least 1 skill, got: {skills}"
