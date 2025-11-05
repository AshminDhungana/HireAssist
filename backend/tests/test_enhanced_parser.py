import os
import pytest
from app.services.resumeparser import ResumeParser, FileParseError
from app.schemas.resumes import ParseResumeResponse, PersonalInfo, ExperienceEntry, EducationEntry
from tests.create_test_files import create_test_resume

@pytest.fixture(scope="session")
def sample_pdf(tmp_path_factory):
    # Create test files in session-scoped temp directory
    tmp_path = tmp_path_factory.mktemp("testdata")
    create_test_resume(tmp_path)
    yield os.path.join(tmp_path, "test_resume.pdf")

@pytest.fixture(scope="session")
def encrypted_pdf(sample_pdf):
    # We use the same fixture directory as sample_pdf
    tmp_path = os.path.dirname(sample_pdf)
    return os.path.join(tmp_path, "encrypted.pdf")


@pytest.fixture(scope="session")
def sample_docx(sample_pdf):
    # DOCX created alongside sample_pdf by the generator
    tmp_path = os.path.dirname(sample_pdf)
    return os.path.join(tmp_path, "test_resume.docx")

# Sample test data
SAMPLE_TEXT_WITH_EXPERIENCE = """
John Doe
Software Engineer at Tech Corp
2020-2023
Led backend development team and implemented new features
Previous Experience:
Data Engineer at Data Inc
2018-2020
Worked with big data and analytics
"""

SAMPLE_TEXT_WITH_EDUCATION = """
Education:
B.S. Computer Science
University of Technology
2014-2018

M.S. Software Engineering
Tech Institute
2019-2021
"""

SAMPLE_TEXT_WITH_SKILLS = """
Skills:
Python, FastAPI, SQL, Docker, Kubernetes
Experience with Machine Learning and Data Science
"""

def test_experience_extraction(sample_pdf):
    parser = ResumeParser()
    text = parser.extract_text_from_pdf(sample_pdf)
        
    experiences = parser.extract_experience(text)
    
    assert isinstance(experiences, list)
    assert len(experiences) >= 1, "Should find at least 1 experience entry"
    
    # Check structure of first experience
    first_exp = experiences[0]
    assert isinstance(first_exp, dict)
    assert all(key in first_exp for key in ['company', 'title', 'dates'])
    
    # Verify content
    assert any('tech corp' in exp.get('company', '').lower() for exp in experiences)
    assert any('senior developer' in exp.get('title', '').lower() for exp in experiences)
    assert any('2020-2023' in exp.get('dates', '') for exp in experiences)

def test_education_extraction(sample_pdf):
    parser = ResumeParser()
    text = parser.extract_text_from_pdf(sample_pdf)
        
    education = parser.extract_education(text)
    
    assert isinstance(education, list)
    assert len(education) >= 1, "Should find at least 1 education entry"
    
    # Check structure
    first_edu = education[0]
    assert isinstance(first_edu, dict)
    assert all(key in first_edu for key in ['degree', 'institution', 'dates'])
    
    # Verify content
    assert any('computer science' in edu.get('degree', '').lower() for edu in education)
    assert any('tech university' in edu.get('institution', '').lower() for edu in education)
    assert any('2015-2019' in edu.get('dates', '') for edu in education)

def test_confidence_scoring(sample_pdf):
    parser = ResumeParser()
    parsed = parser.parse_resume(sample_pdf, "application/pdf")
    
    assert 'confidence_score' in parsed
    assert isinstance(parsed['confidence_score'], float)
    assert 0 <= parsed['confidence_score'] <= 1

def test_schema_validation(sample_pdf):
    """Test that parser output validates against our Pydantic schemas"""
    parser = ResumeParser()
    parsed = parser.parse_resume(sample_pdf, "application/pdf")
    
    # Should not raise validation errors
    response = ParseResumeResponse(**parsed)
    
    assert isinstance(response.personal_info, PersonalInfo)
    assert isinstance(response.experience, list)
    assert all(isinstance(exp, ExperienceEntry) for exp in response.experience)
    assert isinstance(response.education, list)
    assert all(isinstance(edu, EducationEntry) for edu in response.education)

def test_error_handling(encrypted_pdf):
    parser = ResumeParser()
    
    # Test encrypted PDF handling
    with pytest.raises(FileParseError) as exc_info:
        text = parser.extract_text_from_pdf(encrypted_pdf)
    assert "encrypted" in str(exc_info.value).lower()
    
    # Test invalid file type - parse_resume returns structured error for unsupported types
    parsed = parser.parse_resume(encrypted_pdf, "text/plain")
    assert isinstance(parsed, dict)
    assert parsed.get('error') is not None
    assert 'unsupported' in str(parsed.get('error')).lower()

def test_detailed_extraction(sample_pdf):
    parser = ResumeParser()
    parsed = parser.parse_resume(sample_pdf, "application/pdf")
    
    # Check detailed experience fields
    assert isinstance(parsed.get('experience'), list), "Experience should be a list"
    assert len(parsed['experience']) > 0, "Should have at least one experience entry"
    exp_entry = parsed['experience'][0]
    assert isinstance(exp_entry, dict)
    assert all(key in exp_entry for key in ['company', 'title', 'dates']), f"Keys missing from {exp_entry}"
    assert exp_entry['title'].lower() == "senior developer"
    assert exp_entry['company'].lower() == "tech corp"
    assert exp_entry['dates'] == "2020-2023"
    
    # Check detailed education fields
    assert isinstance(parsed.get('education'), list), "Education should be a list"
    assert len(parsed['education']) > 0, "Should have at least one education entry"
    edu_entry = parsed['education'][0]
    assert isinstance(edu_entry, dict)
    assert all(key in edu_entry for key in ['degree', 'institution', 'dates']), f"Keys missing from {edu_entry}"
    assert "computer science" in edu_entry['degree'].lower()
    assert "tech university" in edu_entry['institution'].lower()
    assert edu_entry['dates'] == "2015-2019"

def test_spacy_ner_enrichment(sample_pdf):
    parser = ResumeParser()
    parsed = parser.parse_resume(sample_pdf, "application/pdf")
    
    # Check NER enriched fields when spaCy is available
    if parser.nlp:
        personal_info = parsed.get('personal_info', {})
        assert 'name' in personal_info


def test_docx_parsing(sample_docx):
    parser = ResumeParser()
    # Use the common DOCX mimetype for Office Open XML
    parsed = parser.parse_resume(sample_docx, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    assert isinstance(parsed, dict)
    assert 'experience' in parsed and isinstance(parsed['experience'], list)
    assert len(parsed['experience']) > 0


def test_skill_aliases_and_typos_extraction():
    parser = ResumeParser()
    text = (
        "Experienced in Pyton, js, ReactJS, NodeJS, Kubernates, Postgressql.\n"
        "Also familiar with TF and NLP."
    )
    skills = parser.extract_skills(text)

    # Expect canonicalized skill names from aliases/typos
    expected = {"Python", "JavaScript", "React", "Node.js", "Kubernetes", "PostgreSQL", "TensorFlow", "NLP"}
    assert expected.issubset(set(skills)), f"Missing expected skills. Got: {skills}"