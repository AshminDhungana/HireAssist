import spacy
from typing import Dict, Any, List, Optional
from pypdf import PdfReader
from docx import Document
import re
import os
import json
import logging
from difflib import SequenceMatcher

try:
    import pdfplumber
except Exception:
    pdfplumber = None

logger = logging.getLogger(__name__)


class FileParseError(Exception):
    pass


class SkillsStandardizer:
    """Standardize and normalize skills against skills database"""
    
    def __init__(self, skill_database: List[str]):
        self.skill_database = skill_database
        self.skills_lower = {s.lower(): s for s in skill_database}
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name to match database"""
        if not skill:
            return ""
        
        skill_lower = skill.lower().strip()
        
        # Exact match (fastest)
        if skill_lower in self.skills_lower:
            return self.skills_lower[skill_lower]
        
        # Fuzzy match for typos/variations (e.g., "pyton" → "Python")
        best_match = None
        best_ratio = 0.0
        
        for db_skill_lower, db_skill in self.skills_lower.items():
            ratio = SequenceMatcher(None, skill_lower, db_skill_lower).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = db_skill
        
        # Return fuzzy match if similarity > 0.8 (80%)
        if best_ratio > 0.8:
            return best_match
        
        # Return original if no good match
        return skill
    
    def standardize_skills(self, skills: List[str]) -> List[str]:
        """Normalize and deduplicate skills"""
        if not skills:
            return []
        
        standardized = set()
        for skill in skills:
            normalized = self.normalize_skill(skill)
            if normalized:
                standardized.add(normalized)
        
        return sorted(list(standardized))


class ResumeParser:
    def __init__(self):
        # Load spaCy model (prefer transformer if available).
        try:
            self.nlp = spacy.load("en_core_web_trf")
        except Exception:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                logger.warning("spaCy models not available; continuing without spaCy NER")
                self.nlp = None

        # Load skill database from file if available
        self.skill_database = self._load_skill_database()
        
        # ✅ NEW: Initialize skills standardizer
        self.skills_standardizer = SkillsStandardizer(self.skill_database)

        # Build a normalization map from possible aliases/synonyms to canonical skill names
        try:
            self.skill_map = self._build_skill_map(self.skill_database)
        except Exception:
            logger.exception("Failed to build skill normalization map; falling back to simple list")
            self.skill_map = {}

    def extract_text_from_pdf(self, filepath: str) -> str:
        """Extract text from PDF. Use pypdf first, fallback to pdfplumber if available."""
        text = ""
        try:
            with open(filepath, "rb") as file:
                pdfreader = PdfReader(file)
                if getattr(pdfreader, "is_encrypted", True):
                    logger.exception("PDF is encrypted or password-protected: %s", filepath)
                    raise FileParseError("PDF is encrypted or password-protected")
                for page in pdfreader.pages:
                    page_text = page.extract_text() or ""
                    text += page_text
            if not text and pdfplumber:
                try:
                    with pdfplumber.open(filepath) as pdf:
                        for p in pdf.pages:
                            page_text = p.extract_text() or ""
                            text += page_text
                except Exception as e:
                    logger.exception("pdfplumber fallback failed: %s", e)
                    raise FileParseError("Unable to extract text from PDF")
        except FileParseError:
            raise
        except Exception as e:
            logger.exception("pypdf extraction failed for %s: %s", filepath, e)
            if pdfplumber:
                try:
                    with pdfplumber.open(filepath) as pdf:
                        for p in pdf.pages:
                            page_text = p.extract_text() or ""
                            text += page_text
                except Exception as e2:
                    logger.exception("pdfplumber also failed for %s: %s", filepath, e2)
                    raise FileParseError("Unable to extract text from PDF")
            else:
                raise FileParseError("Unable to extract text from PDF")

        if not text:
            raise FileParseError("PDF contains no extractable text")

        return text

    def extract_text_from_docx(self, filepath: str) -> str:
        try:
            doc = Document(filepath)
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)
        except Exception as e:
            logger.exception("DOCX extraction failed for %s: %s", filepath, e)
            raise FileParseError("Unable to extract text from DOCX")

    def extract_email(self, text: str) -> Optional[str]:
        email_pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None

    def extract_phone(self, text: str) -> Optional[str]:
        phone_pattern = r"\+?\d[\d\s().-]{7,}\d"
        phones = re.findall(phone_pattern, text)
        return phones[0] if phones else None

    def extract_skills(self, text: str) -> List[str]:
        """Extract and standardize skills from text"""
        if not text:
            return []

        def normalize(s: str) -> str:
            return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).strip()

        norm_text = normalize(text)
        words = norm_text.split()
        found = []

        # Build n-grams up to 4 words
        max_ngram = 4
        for n in range(1, max_ngram + 1):
            for i in range(len(words) - n + 1):
                ngram = " ".join(words[i : i + n])
                if not ngram:
                    continue
                if ngram in self.skill_map:
                    canonical = self.skill_map[ngram]
                    if canonical not in found:
                        found.append(canonical)

        # Also check for direct substring matches
        for canonical in self.skill_database:
            try:
                norm_canon = normalize(canonical)
                if norm_canon and norm_canon in norm_text and canonical not in found:
                    found.append(canonical)
            except Exception:
                continue

        # ✅ STANDARDIZE extracted skills
        standardized = self.skills_standardizer.standardize_skills(found)
        
        logger.info(f"Extracted {len(found)} skills, standardized to {len(standardized)}")
        
        return standardized

    def _build_skill_map(self, skills_source: List[str]) -> Dict[str, str]:
        """Create a mapping of normalized alias -> canonical skill name."""
        def normalize_key(s: str) -> str:
            return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).strip()

        skill_map: Dict[str, str] = {}

        builtin_synonyms = {
            "py": "Python",
            "python3": "Python",
            "python2": "Python",
            "js": "JavaScript",
            "tsx": "TypeScript",
            "ts": "TypeScript",
            "tf": "TensorFlow",
            "nlp": "NLP",
            "cv": "OpenCV",
            "dockercompose": "Docker Compose",
            "k8s": "Kubernetes",
        }

        for entry in skills_source:
            if isinstance(entry, str):
                canon = entry
            elif isinstance(entry, dict) and "name" in entry:
                canon = entry["name"]
            else:
                continue

            norm = normalize_key(canon)
            if norm:
                skill_map[norm] = canon

            for part in norm.split():
                if part and part not in skill_map:
                    skill_map[part] = canon

        for alias, canon in builtin_synonyms.items():
            skill_map[normalize_key(alias)] = canon

        return skill_map

    def _extract_with_spacy(self, text: str) -> Dict[str, Optional[str]]:
        """Use spaCy NER to enrich personal/company info when model is available."""
        out = {"name": None, "company": None}
        if not self.nlp:
            return out

        try:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON" and not out["name"]:
                    out["name"] = ent.text
                if ent.label_ == "ORG" and not out["company"]:
                    out["company"] = ent.text
                if out["name"] and out["company"]:
                    break
        except Exception as e:
            logger.exception("spaCy NER failed: %s", e)

        return out

    def extract_experience(self, text: str) -> List[Dict[str, Optional[str]]]:
        """Extract structured work experience entries from text."""
        experiences = []
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        
        date_pattern = r"(?:\d{4}[-–]\d{4}|\d{4}\s*[-–]\s*(?:present|current|now)|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})"
        title_pattern = r"\b(Senior|Lead|Principal|Staff|Software|Developer|Engineer|Manager|Director|Architect|Consultant)\b"
        
        current_entry = {}
        for line in lines:
            if len(line) < 10:
                continue
                
            if re.search(date_pattern, line, re.IGNORECASE):
                if current_entry:
                    experiences.append(current_entry)
                current_entry = {"dates": re.search(date_pattern, line, re.IGNORECASE).group()}
                
                if re.search(title_pattern, line):
                    parts = re.split(date_pattern, line)
                    if len(parts) >= 2:
                        current_entry["title"] = parts[0].strip()
                        current_entry["company"] = parts[1].strip()
            
            elif current_entry:
                if "title" not in current_entry and re.search(title_pattern, line):
                    current_entry["title"] = line.strip()
                elif "company" not in current_entry and not re.search(date_pattern, line):
                    current_entry["company"] = line.strip()
                
                if "title" in current_entry and "company" in current_entry:
                    current_entry.setdefault("description", line.strip())
        
        if current_entry:
            experiences.append(current_entry)
        
        clean_experiences = []
        seen = set()
        for exp in experiences:
            key = (exp.get("company", ""), exp.get("title", ""), exp.get("dates", ""))
            if key not in seen:
                seen.add(key)
                clean_experiences.append(exp)
        
        return clean_experiences[:10]

    def extract_education(self, text: str) -> List[Dict[str, Optional[str]]]:
        """Extract structured education entries from text."""
        education = []
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        
        degree_pattern = r"\b(BS|BA|B\.Sc|MS|M\.Sc|PhD|MBA|Bachelor|Master|Doctor|Associate|Diploma|Certificate)\b"
        date_pattern = r"(?:\d{4}[-–]\d{4}|\d{4})"
        institution_keywords = r"\b(University|College|Institute|School)\b"
        
        current_entry = {}
        for line in lines:
            if len(line) < 10:
                continue
                
            if re.search(degree_pattern, line, re.IGNORECASE):
                if current_entry:
                    education.append(current_entry)
                current_entry = {"degree": line.strip()}
                
                if re.search(date_pattern, line):
                    current_entry["dates"] = re.search(date_pattern, line).group()
                if re.search(institution_keywords, line, re.IGNORECASE):
                    inst_match = re.search(fr".*?({institution_keywords}).*?(?={date_pattern}|\Z)", line, re.IGNORECASE)
                    if inst_match:
                        current_entry["institution"] = inst_match.group().strip()
            
            elif current_entry:
                if "dates" not in current_entry and re.search(date_pattern, line):
                    current_entry["dates"] = re.search(date_pattern, line).group()
                elif "institution" not in current_entry and re.search(institution_keywords, line, re.IGNORECASE):
                    current_entry["institution"] = line.strip()
        
        if current_entry:
            education.append(current_entry)
        
        clean_education = []
        seen = set()
        for edu in education:
            key = (edu.get("degree", ""), edu.get("institution", ""), edu.get("dates", ""))
            if key not in seen:
                seen.add(key)
                clean_education.append(edu)
        
        return clean_education[:10]

    def calculate_experience_years(self, text: str) -> int:
        pattern = r"(\d+)\s*(?:\+)?\s*years?\s+(?:of\s+)?experience"
        matches = re.findall(pattern, text.lower())
        if matches:
            years = [int(m) for m in matches if m.isdigit()]
            return max(years) if years else 0
        ranges = re.findall(r"(\d{4})\s*[-–]\s*(\d{4})", text)
        total = 0
        for start, end in ranges:
            try:
                total += int(end) - int(start)
            except Exception:
                continue
        return total

    def parse_resume(self, filepath: str, mimetype: str) -> Dict[str, Any]:
        """Parse resume and return structured data matching ParseResumeResponse schema."""
        try:
            if mimetype == "application/pdf":
                text = self.extract_text_from_pdf(filepath)
            elif mimetype.endswith("wordprocessingml.document") or filepath.lower().endswith('.docx'):
                text = self.extract_text_from_docx(filepath)
            else:
                raise FileParseError(f"Unsupported file type: {mimetype}")

            spacy_info = self._extract_with_spacy(text)
            
            personal_info = {
                "name": spacy_info.get("name"),
                "email": self.extract_email(text),
                "phone": self.extract_phone(text),
                "location": None
            }

            experience_entries = self.extract_experience(text)
            education_entries = self.extract_education(text)
            
            # ✅ Extract and standardize skills
            skills = self.extract_skills(text)

            required_fields = [
                personal_info.get("name"),
                personal_info.get("email"),
                bool(experience_entries),
                bool(education_entries)
            ]
            confidence_score = sum(1 for f in required_fields if f) / len(required_fields)

            parsed_data = {
                "raw_text": text,
                "personal_info": personal_info,
                "skills": skills,  # ✅ Now standardized!
                "experience": experience_entries,
                "education": education_entries,
                "experience_years": self.calculate_experience_years(text),
                "confidence_score": round(confidence_score, 2),
                "error": None
            }

            return parsed_data
            
        except FileParseError as e:
            return {
                "raw_text": None,
                "personal_info": None,
                "skills": [],
                "experience": [],
                "education": [],
                "experience_years": None,
                "confidence_score": 0.0,
                "error": str(e)
            }
        except Exception as e:
            logger.exception("Unexpected error parsing resume")
            return {
                "raw_text": None,
                "personal_info": None,
                "skills": [],
                "experience": [],
                "education": [],
                "experience_years": None,
                "confidence_score": 0.0,
                "error": f"Unexpected error: {str(e)}"
            }

    def _load_skill_database(self) -> List[str]:
        """Load skills from skills.json"""
        base_dir = os.path.dirname(__file__)
        skills_file = os.path.join(base_dir, "skills.json")
        
        if os.path.exists(skills_file):
            try:
                with open(skills_file, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    # Handle both list and dict formats
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and "skills" in data:
                        return data["skills"]
            except Exception as e:
                logger.exception("Failed to load skills.json: %s", e)

        # Fallback hardcoded list
        logger.warning("Using fallback skills list - skills.json not found or invalid")
        return [
            "Python", "JavaScript", "TypeScript", "React", "Node.js", "FastAPI",
            "Django", "Flask", "SQL", "PostgreSQL", "MySQL", "MongoDB",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
            "Git", "CI/CD", "Jenkins", "CircleCI", "Data Science", "Machine Learning",
            "Pandas", "NumPy", "scikit-learn", "PyTorch", "TensorFlow", "NLP",
            "Redis", "Kafka", "GraphQL", "REST", "HTML", "CSS", "Tailwind",
            "React Native", "Flutter", "iOS", "Android", "Java", "C++", "Go"
        ]
