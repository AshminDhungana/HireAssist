"""
Enhanced Regex-based Resume Parser (Parser B)
Fast alternative to NLP parser with ~1.3ms processing time
"""

import re
from typing import List, Optional, Dict, Any
import time


class SimpleParser:
    """
    Fast regex-based resume parser.
    
    Performance: ~1.3ms per resume
    Trade-off: Less accurate than NLP-based Parser A, but much faster
    
    Handles:
    - Contact info (phone, email)
    - Education (degrees, institutions, graduation years)
    - Skills (from predefined database)
    """
    
    def __init__(self):
        """Initialize parser with compiled regex patterns"""
        self.phone_patterns = self._compile_phone_patterns()
        self.education_patterns = self._compile_education_patterns()
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            re.IGNORECASE
        )
        
        # Load skills database
        self.skills_database = self._load_skills_database()
    
    def _compile_phone_patterns(self) -> List[re.Pattern]:
        """
        Compile phone number patterns for different formats.
        
        Handles:
        - US/Canada: (555) 123-4567, 555-123-4567, 5551234567
        - International: +1 555 123 4567, +44 20 7946 0958
        - Extensions: x123, ext.123, ext 123
        """
        patterns = [
            # US/Canada with parentheses: (555) 123-4567
            r'\((\d{3})\)\s*[-.]?(\d{3})[-.]?(\d{4})',
            
            # US/Canada with hyphens/dots: 555-123-4567 or 555.123.4567
            r'(\d{3})[-. ](\d{3})[-. ](\d{4})',
            
            # US/Canada without formatting: 5551234567
            r'\b(\d{3})(\d{3})(\d{4})\b',
            
            # International format: +1 555 123 4567
            r'\+(\d{1,3})\s?(\d{1,4})\s?(\d{3})\s?(\d{3})\s?(\d{4})',
            
            # UK format: +44 20 7946 0958
            r'\+44\s?[0-9]{1,4}\s?[0-9]{6,8}',
            
            # Phone with extension: 555-123-4567 x123
            r'(\d{3})[-. ]?(\d{3})[-. ]?(\d{4})\s*(?:x|ext\.?|ext)\s*(\d{3,5})',
        ]
        
        return [re.compile(p, re.IGNORECASE) for p in patterns]
    
    def _compile_education_patterns(self) -> Dict[str, re.Pattern]:
        """
        Compile education-related regex patterns.
        
        Extracts:
        - Degree types: BS, B.S., Bachelor of Science, MBA, Ph.D., etc.
        - Graduation years: 2020, Class of 2020, Expected May 2020
        - Universities/Colleges: MIT, University of Michigan, etc.
        """
        return {
            # Degree patterns: B.S., Bachelor, Master's, MBA, Ph.D., Associate
            'degree': re.compile(
                r'\b(?:'
                r'(?:B\.?S\.?|B\.?A\.?|B\.?E\.?|B\.?Sc\.?|B\.?Com\.?)'
                r'|(?:M\.?S\.?|M\.?A\.?|M\.?E\.?|M\.?Sc\.?|M\.?B\.?A\.?|MBA)'
                r'|(?:Ph\.?D\.?|D\.?M\.?D\.?|M\.?D\.?)'
                r"|(?:Associate's?|Associate Degree)"
                r"|(?:Bachelor's?|Master's?)"
                r')\b',
                re.IGNORECASE
            ),
            
            # Field of study patterns (follows degree)
            'field': re.compile(
                r'(?:in|of)\s+([A-Za-z\s&]+?)(?=,|;|\.|$|in\s+|at\s+)',
                re.IGNORECASE
            ),
            
            # University/College names - capitalized words followed by University/College
            'institution': re.compile(
                r'(?:(?:from|at|at\s+)?'
                r'([A-Z][a-z\s&]+(?:University|College|Institute|School|Academy|Polytechnic)))',
                re.IGNORECASE
            ),
            
            # Graduation year patterns
            'graduation_year': re.compile(
                r'(?:'
                r'(?:Class\s+of\s+)?(\d{4})|'
                r'(?:Graduated?\s+)(\d{4})|'
                r'(?:Expected\s+)(?:.*\s+)?(\d{4})|'
                r'(?:Expected graduation[:\s]+)(\d{4})|'
                r'(?:May|June|July|August|September|October|November|December)\s+(\d{4})'
                r')\b',
                re.IGNORECASE
            ),
        }
    
    def _load_skills_database(self) -> Dict[str, List[str]]:
        """
        Load skills database.
        In production, this would load from data/skills_database.json
        """
        return {
            'programming_languages': [
                'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Ruby', 'Go', 'Rust',
                'PHP', 'Swift', 'Kotlin', 'SQL', 'R', 'MATLAB', 'Scala', 'Perl'
            ],
            'web_frameworks': [
                'React', 'Vue', 'Angular', 'Django', 'FastAPI', 'Flask', 'Express',
                'Spring', 'ASP.NET', 'Ruby on Rails', 'Laravel', 'Symfony'
            ],
            'databases': [
                'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
                'Firebase', 'DynamoDB', 'Oracle', 'SQL Server', 'Cassandra'
            ],
            'tools_platforms': [
                'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Git', 'Jenkins',
                'Terraform', 'Ansible', 'CI/CD'
            ],
            'soft_skills': [
                'Leadership', 'Communication', 'Problem Solving', 'Team Work',
                'Project Management', 'Agile', 'Scrum', 'Critical Thinking'
            ]
        }
    
    # ===== PHONE EXTRACTION =====
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract first phone number found"""
        if not text:
            return None
        
        for pattern in self.phone_patterns:
            match = pattern.search(text)
            if match:
                return match.group(0).strip()
        
        return None
    
    def extract_all_phones(self, text: str) -> List[str]:
        """Extract all phone numbers"""
        if not text:
            return []
        
        phones = set()
        for pattern in self.phone_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                phone = match.group(0).strip()
                phones.add(phone)
        
        return list(phones)
    
    # ===== EMAIL EXTRACTION =====
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract first email found"""
        if not text:
            return None
        
        match = self.email_pattern.search(text)
        return match.group(0) if match else None
    
    def extract_all_emails(self, text: str) -> List[str]:
        """Extract all emails"""
        if not text:
            return []
        
        return self.email_pattern.findall(text)
    
    # ===== EDUCATION EXTRACTION =====
    
    def extract_education_section(self, text: str) -> str:
        """Extract education section from resume"""
        education_markers = r'(?:EDUCATION|ACADEMIC|QUALIFICATIONS|DEGREES|SCHOOLING)'
        section_markers = r'(?:EXPERIENCE|WORK|EMPLOYMENT|SKILLS|PROJECTS|CERTIFICATIONS|SUMMARY)'
        
        match = re.search(
            f'{education_markers}[^\n]*\n(.*?)(?=\n\n?{section_markers}|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        
        return match.group(1) if match else text
    
    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract all education entries"""
        education_list = []
        
        # Get education section
        edu_section = self.extract_education_section(text)
        
        # Split entries by double newline or bullet points
        entries = re.split(r'\n\s*\n|•|\*', edu_section)
        
        for entry in entries:
            if not entry.strip():
                continue
            
            edu_entry = {}
            
            # Extract degree
            degree_match = self.education_patterns['degree'].search(entry)
            if degree_match:
                edu_entry['degree'] = degree_match.group(0).strip()
            
            # Extract field
            if degree_match:
                remaining = entry[degree_match.end():]
                field_match = self.education_patterns['field'].search(remaining)
                if field_match:
                    edu_entry['field'] = field_match.group(1).strip()
            
            # Extract institution
            institution_match = self.education_patterns['institution'].search(entry)
            if institution_match:
                edu_entry['institution'] = institution_match.group(1).strip()
            
            # Extract graduation year
            for match in self.education_patterns['graduation_year'].finditer(entry):
                year = next((g for g in match.groups() if g), None)
                if year:
                    try:
                        year_int = int(year)
                        if 1950 <= year_int <= 2030:
                            edu_entry['graduation_year'] = year_int
                            break
                    except ValueError:
                        continue
            
            if edu_entry:
                education_list.append(edu_entry)
        
        return education_list
    
    # ===== SKILLS EXTRACTION =====
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills from all categories"""
        text_lower = text.lower()
        found_skills = {}
        
        for category, skills in self.skills_database.items():
            found_skills[category] = [
                skill for skill in skills
                if skill.lower() in text_lower
            ]
        
        return found_skills
    
    def get_all_skills(self, text: str) -> List[str]:
        """Get flat list of all found skills"""
        skills_by_category = self.extract_skills(text)
        return [
            skill
            for skills in skills_by_category.values()
            for skill in skills
        ]
    
    # ===== MAIN PARSE FUNCTION =====
    
    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse complete resume and return structured data.
        
        Returns:
            {
                'personal_info': {'phone': '...', 'email': '...'},
                'education': [...],
                'skills': {...},
                'all_skills': [...],
                'parsing_time_ms': ...,
            }
        """
        start_time = time.time()
        
        parsed_data = {
            'personal_info': {
                'phone': self.extract_phone(text),
                'email': self.extract_email(text),
                'all_phones': self.extract_all_phones(text),
                'all_emails': self.extract_all_emails(text),
            },
            'education': self.extract_education(text),
            'skills': self.extract_skills(text),
            'all_skills': self.get_all_skills(text),
            'parsing_time_ms': round((time.time() - start_time) * 1000, 2),
        }
        
        return parsed_data
    
        # ===== COMPATIBILITY METHODS =====
    
    def parse_resume(self, file_path: str, content_type: str) -> Dict[str, Any]:
        """
        Compatibility method for comparison script.
        Extracts text from PDF/DOCX and calls parse()
        
        Args:
            file_path: Path to resume file
            content_type: MIME type (application/pdf or wordprocessingml.document)
        
        Returns:
            Parsed resume data in expected format
        """
        # Extract text from file
        text = self._extract_text_from_file(file_path, content_type)
        
        # Parse using new API
        parsed = self.parse(text)
        
        # Convert to expected format (match ResumeParser output)
        return {
            "personal_info": {
                "email": parsed["personal_info"]["email"],
                "phone": parsed["personal_info"]["phone"],
                "name": None  # Could extract name if needed
            },
            "skills": parsed["all_skills"],  # Flat list
            "experience": [],  # Not implemented yet
            "education": parsed["education"],
            "experience_years": 0,  # Could calculate from education years
        }
    
    def _extract_text_from_file(self, file_path: str, content_type: str) -> str:
        """Extract text from PDF or DOCX file"""
        if content_type == 'application/pdf':
            return self._extract_pdf_text(file_path)
        elif 'wordprocessingml' in content_type:
            return self._extract_docx_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {content_type}")
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF using PyPDF2"""
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
        """Extract text from DOCX using python-docx"""
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            raise ValueError(f"DOCX extraction failed: {e}")

