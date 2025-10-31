import pytest
from app.services.resumeparser import ResumeParser


def test_normalize_py_and_js():
    rp = ResumeParser()
    text = "Experienced backend engineer with 5+ years working with py and js."
    skills = rp.extract_skills(text)
    assert "Python" in skills
    assert "JavaScript" in skills


def test_multiword_skill_detection():
    rp = ResumeParser()
    text = "Built complex systems using docker compose and kubernetes clusters."
    skills = rp.extract_skills(text)
    assert "Docker Compose" in skills or "Docker" in skills
    assert "Kubernetes" in skills


def test_no_false_positives_on_empty_text():
    rp = ResumeParser()
    skills = rp.extract_skills("")
    assert skills == []
