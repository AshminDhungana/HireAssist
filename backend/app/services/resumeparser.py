import spacy
from typing import Dict, Any, List
import PyPDF2
from docx import Document
import re

class ResumeParser:
    def __init__(self):
        # Load spaCy model with custom NER if available
        try:
            self.nlp = spacy.load("en_core_web_trf")
        except Exception:
            self.nlp = spacy.load("en_core_web_sm")
        self.skill_database = self.load_skill_database()
    
    def extract_text_from_pdf(self, filepath: str) -> str:
        text = ""
        with open(filepath, "rb") as file:
            pdfreader = PyPDF2.PdfReader(file)
            for page in pdfreader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        return text

    def extract_text_from_docx(self, filepath: str) -> str:
        doc = Document(filepath)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)

    def extract_email(self, text: str) -> str:
        email_pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None

    def extract_phone(self, text: str) -> str:
        phone_pattern = r"\+?\d{1,3}[-.\s]?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}"
        phones = re.findall(phone_pattern, text)
        return phones[0] if phones else None

    def extract_skills(self, text: str) -> List[str]:
        doc = self.nlp(text)
        skills = []
        # spaCy NER extraction
        for ent in doc.ents:
            if ent.label_ == "SKILL":
                skills.append(ent.text)
        # Keyword matching from skill DB
        text_lower = text.lower()
        for skill in self.skill_database:
            if skill.lower() in text_lower:
                skills.append(skill)
        return list(set(skills))  # Remove duplicates

    def extract_experience(self, text: str) -> List[str]:
        doc = self.nlp(text)
        experiences = []
        for ent in doc.ents:
            if ent.label_ == "WORK_EXPERIENCE":
                experiences.append(ent.text)
        # Fallback pattern (years, companies, positions)
        # Can be expanded as needed
        return experiences

    def extract_education(self, text: str) -> List[str]:
        doc = self.nlp(text)
        education = []
        for ent in doc.ents:
            if ent.label_ in ["DEGREE", "EDUCATION"]:
                education.append(ent.text)
        # Fallback pattern (degrees, schools, dates)
        return education

    def calculate_experience_years(self, text: str) -> int:
        # Look for patterns like "X years of experience"
        pattern = r"(\d+)\s+years?\s+of\s+experience"
        matches = re.findall(pattern, text.lower())
        years = [int(m) for m in matches if m.isdigit()]
        return max(years) if years else 0

    def load_skill_database(self) -> List[str]:
        # In production, load from DB or file
        # Example base skill list:
        return [
            "Python", "JavaScript", "React", "FastAPI", "Django", "Machine Learning",
            "Data Science", "SQL", "PostgreSQL", "AWS", "Docker", "Kubernetes", "Git", "CI/CD"
        ]

    def calculate_confidence_scores(self, text: str) -> Dict[str, float]:
        # Placeholder - you can refine with custom logic/testing
        return {
            "overall": 0.85,
            "skills": 0.90,
            "experience": 0.80,
            "education": 0.85,
        }

    def parse_resume(self, filepath: str, mimetype: str) -> Dict[str, Any]:
        # Extract text depending on file type
        if mimetype == "application/pdf":
            text = self.extract_text_from_pdf(filepath)
        elif mimetype.endswith("wordprocessingml.document"):
            text = self.extract_text_from_docx(filepath)
        else:
            raise ValueError(f"Unsupported file type: {mimetype}")
        
        # Parse structured data
        parsed_data = {
            "raw_text": text,
            "personal_info": {
                "email": self.extract_email(text),
                "phone": self.extract_phone(text),
            },
            "skills": self.extract_skills(text),
            "experience": self.extract_experience(text),
            "education": self.extract_education(text),
            "experience_years": self.calculate_experience_years(text),
            "confidence_scores": self.calculate_confidence_scores(text)
        }
        return parsed_data
