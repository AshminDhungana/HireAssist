from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PersonalInfo(BaseModel):
    """Contact and personal information extracted from resume."""
    name: Optional[str] = Field(None, description="Full name extracted from resume")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number in any format")
    location: Optional[str] = Field(None, description="Location if detected")


class ExperienceEntry(BaseModel):
    """A single work experience entry."""
    company: Optional[str] = Field(None, description="Company name")
    title: Optional[str] = Field(None, description="Job title")
    dates: Optional[str] = Field(None, description="Date range or duration")
    description: Optional[str] = Field(None, description="Role description if available")


class EducationEntry(BaseModel):
    """A single education entry."""
    degree: Optional[str] = Field(None, description="Degree name/type")
    institution: Optional[str] = Field(None, description="School/university name")
    dates: Optional[str] = Field(None, description="Date range or graduation date")


class ParseResumeRequest(BaseModel):
    """Optional parameters for resume parsing."""
    use_rag: bool = Field(False, description="Whether to use RAG/LLM parser")
    extract_detailed: bool = Field(False, description="Whether to extract detailed sections")


class ParseResumeResponse(BaseModel):
    """Structured response from resume parsing."""
    raw_text: Optional[str] = Field(None, description="Raw text extracted from document")
    personal_info: Optional[PersonalInfo] = Field(None, description="Contact and personal details")
    skills: List[str] = Field(default_factory=list, description="List of detected skills")
    experience: List[ExperienceEntry] = Field(default_factory=list, description="Work experience entries")
    education: List[EducationEntry] = Field(default_factory=list, description="Education history")
    experience_years: Optional[int] = Field(None, description="Total years of experience detected")
    raw_output: Optional[Any] = Field(None, description="Raw output from parser/LLM")
    error: Optional[str] = Field(None, description="Error message if parsing failed")
    confidence_score: Optional[float] = Field(None, description="Overall confidence in parsing results")

    class Config:
        json_schema_extra = {
            "example": {
                "personal_info": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+1234567890",
                    "location": "New York, NY"
                },
                "skills": ["Python", "FastAPI", "SQL"],
                "experience": [
                    {
                        "company": "Tech Corp",
                        "title": "Senior Developer",
                        "dates": "2020-2023",
                        "description": "Led backend team"
                    }
                ],
                "education": [
                    {
                        "degree": "B.S. Computer Science",
                        "institution": "University of Example",
                        "dates": "2016-2020"
                    }
                ],
                "experience_years": 5,
                "confidence_score": 0.85
            }
        }
