"""
Simple regex-based resume parser (Parser B).
Alternative implementation for comparison with main parser.
"""
import re
from typing import Dict, List, Any
import json
import os


class SimpleParser:
    """Lightweight regex-based resume parser for comparison."""
    
    def __init__(self):
        self.skills_db = self._load_skills()
    
    def _load_skills(self) -> List[str]:
        """Load skills from database."""
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'skills_database.json')
        try:
            with open(db_path, 'r') as f:
                skills_data = json.load(f)
                # Flatten all skills into single list
                all_skills = []
                for category, skills in skills_data.items():
                    all_skills.extend(skills)
                return all_skills
        except:
            return []
    
    def parse_resume(self, file_path: str, content_type: str) -> Dict[str, Any]:
        """
        Parse resume using simple regex patterns.
        
        Args:
            file_path: Path to resume file
            content_type: MIME type
            
        Returns:
            Parsed resume dictionary
        """
        # Extract text from file
        text = self._extract_text(file_path, content_type)
        
        return {
            "personal_info": self._extract_personal_info(text),
            "skills": self._extract_skills(text),
            "experience": self._extract_experience(text),
            "education": self._extract_education(text),
            "experience_years": self._estimate_experience_years(text)
        }
    
    def _extract_text(self, file_path: str, content_type: str) -> str:
        """Extract text from PDF or DOCX."""
        if content_type == 'application/pdf':
            return self._extract_pdf_text(file_path)
        elif 'wordprocessingml' in content_type:
            return self._extract_docx_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {content_type}")
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF using PyPDF2."""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise ValueError(f"PDF extraction failed: {e}")
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX using python-docx."""
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            raise ValueError(f"DOCX extraction failed: {e}")
    
    def _extract_personal_info(self, text: str) -> Dict[str, Any]:
        """Extract personal information using regex."""
        info = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            info['email'] = emails[0]
        
        # Phone pattern (various formats)
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            # Join tuple elements if match returns groups
            info['phone'] = ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]
        
        # Name (assume first line or before email/phone)
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and not re.search(r'[@\d]', line) and len(line.split()) <= 4:
                info['name'] = line
                break
        
        return info
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills by matching against skills database."""
        found_skills = set()
        text_lower = text.lower()
        
        for skill in self.skills_db:
            # Case-insensitive word boundary match
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        
        return sorted(list(found_skills))
    
    def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience entries."""
        experiences = []
        
        # Simple pattern: Look for year ranges like "2020-2023" or "2020-Present"
        experience_pattern = r'(\d{4})\s*[-–]\s*(\d{4}|Present|Current)'
        matches = re.findall(experience_pattern, text, re.IGNORECASE)
        
        for start, end in matches:
            experiences.append({
                "start_year": start,
                "end_year": end,
                "current": end.lower() in ['present', 'current']
            })
        
        return experiences
    
    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education information."""
        education = []
        
        # Degree patterns
        degree_patterns = [
            r"bachelor['\"]?s?\s+(?:of\s+)?(\w+)",
            r"master['\"]?s?\s+(?:of\s+)?(\w+)",
            r"phd|doctorate",
            r"associate['\"]?s?\s+degree"
        ]
        
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                education.append({
                    "degree": match.group(0),
                    "field": match.group(1) if match.lastindex else None
                })
        
        return education
    
    def _estimate_experience_years(self, text: str) -> float:
        """Estimate total years of experience."""
        # Look for explicit mentions
        explicit_pattern = r'(\d+)\+?\s*years?\s+(?:of\s+)?experience'
        matches = re.findall(explicit_pattern, text, re.IGNORECASE)
        if matches:
            return float(matches[0])
        
        # Calculate from date ranges
        experiences = self._extract_experience(text)
        if experiences:
            total_years = 0
            current_year = 2023  # Use current year
            
            for exp in experiences:
                start = int(exp['start_year'])
                if exp['current']:
                    end = current_year
                else:
                    end = int(exp['end_year'])
                
                total_years += (end - start)
            
            return float(total_years)
        
        return 0.0
