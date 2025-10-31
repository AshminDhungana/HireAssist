import spacy
from typing import Dict, Any, List, Optional
from pypdf import PdfReader
from docx import Document
import re
import os
import json
import logging

try:
    import pdfplumber
except Exception:
    pdfplumber = None

logger = logging.getLogger(__name__)


class FileParseError(Exception):
    pass


class ResumeParser:
    def __init__(self):
        # Load spaCy model (prefer transformer if available).
        # If models are not installed in the environment, continue without spaCy
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

        # Build a normalization map from possible aliases/synonyms to canonical skill names
        # This allows short aliases like 'py' or 'js' to map to 'Python' / 'JavaScript'.
        try:
            self.skill_map = self._build_skill_map(self.skill_database)
        except Exception:
            logger.exception("Failed to build skill normalization map; falling back to simple list")
            # fallback: empty map
            self.skill_map = {}

    def extract_text_from_pdf(self, filepath: str) -> str:
        """Extract text from PDF. Use pypdf first, fallback to pdfplumber if available."""
        text = ""
        try:
            with open(filepath, "rb") as file:
                pdfreader = PdfReader(file)
                # Detect encrypted/password-protected PDFs early
                if getattr(pdfreader, "is_encrypted", True):
                    logger.exception("PDF is encrypted or password-protected: %s", filepath)
                    raise FileParseError("PDF is encrypted or password-protected")
                # pypdf may raise for some corrupted files
                for page in pdfreader.pages:
                    page_text = page.extract_text() or ""
                    text += page_text
            if not text and pdfplumber:
                # Try pdfplumber fallback
                try:
                    with pdfplumber.open(filepath) as pdf:
                        for p in pdf.pages:
                            page_text = p.extract_text() or ""
                            text += page_text
                except Exception as e:
                    logger.exception("pdfplumber fallback failed: %s", e)
                    raise FileParseError("Unable to extract text from PDF")
        except FileParseError:
            raise  # Re-raise our custom exceptions
        except Exception as e:
            logger.exception("pypdf extraction failed for %s: %s", filepath, e)
            # Try pdfplumber if available
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
        # Normalize text and search for n-gram matches against the skill map.
        # Return canonical skill names.
        if not text:
            return []

        def normalize(s: str) -> str:
            # Lowercase, remove non-alphanumeric characters except spaces
            return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).strip()

        norm_text = normalize(text)
        words = norm_text.split()
        found = []

        # Build n-grams up to 4 words (covers things like 'docker compose', 'machine learning')
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

        # Also check for direct substring matches for multiword canonical names that may
        # include punctuation or different spacing in source text.
        for canonical in self.skill_database:
            try:
                norm_canon = normalize(canonical)
                if norm_canon and norm_canon in norm_text and canonical not in found:
                    found.append(canonical)
            except Exception:
                continue

        return found

    def _build_skill_map(self, skills_source: List[str]) -> Dict[str, str]:
        """Create a mapping of normalized alias -> canonical skill name.

        Accepts a list of canonical skill names. Populates the map with
        normalized forms and some common short aliases.
        """
        def normalize_key(s: str) -> str:
            return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).strip()

        skill_map: Dict[str, str] = {}

        # Small built-in synonyms to catch common short forms
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

        # Populate map from canonical list
        for entry in skills_source:
            if isinstance(entry, str):
                canon = entry
            elif isinstance(entry, dict) and "name" in entry:
                canon = entry["name"]
            else:
                continue

            norm = normalize_key(canon)
            # Map full normalized canonical to canonical
            if norm:
                skill_map[norm] = canon

            # also map individual words in multi-word skills (e.g., 'docker' -> 'Docker')
            for part in norm.split():
                if part and part not in skill_map:
                    skill_map[part] = canon

        # Add builtin synonyms
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
            # Prefer the first PERSON for a name and first ORG for company
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
        
        # Process work experience section
        in_experience = False
        current_title = None
        current_company = None
        current_dates = None
        
        for line in lines:
            if "Work Experience" in line:
                in_experience = True
                continue
                
            if in_experience and line:
                if "at" in line and any(job in line.lower() for job in ["developer", "engineer", "manager"]):
                    # Split into title and company
                    title_part, company_part = line.split(" at ", 1)
                    current_title = title_part.strip()
                    current_company = company_part.strip()
                elif re.match(r"^(?:19|20)\d{2}[-–](?:19|20)\d{2}", line):
                    current_dates = line.strip()
                    
                    # Add complete entry
                    if all([current_title, current_company, current_dates]):
                        experiences.append({
                            "title": current_title,
                            "company": current_company,
                            "dates": current_dates
                        })
                        current_title = current_company = current_dates = None
                        
        return experiences
        """Extract structured work experience entries from text."""
        experiences = []
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        
        # First join lines into a single text preserving newlines
        combined_text = "\n".join(lines)
        
        # Look for patterns like "title at company date"
        exp_pattern = r"(.*?)\s+at\s+(.*?)\s+((?:19|20)\d{2}[-–](?:19|20)\d{2}|(?:19|20)\d{2}[-–](?:present|current|now))"
        matches = re.finditer(exp_pattern, combined_text, re.IGNORECASE | re.MULTILINE)
        
        for match in matches:
            title, company, dates = match.groups()
            if all(x.strip() for x in [title, company, dates]):
                experiences.append({
                    "title": title.strip(),
                    "company": company.strip(),
                    "dates": dates.strip()
                })
        """Extract structured work experience entries from text."""
        experiences = []
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        
        date_pattern = r"((?:19|20)\d{2}[-–]\d{4}|(?:19|20)\d{2}[-–](?:present|current|now))"
        title_pattern = r"(Senior|Lead|Principal|Staff|Software|Developer|Engineer|Manager|Director|Architect|Consultant)"
        at_pattern = r"\s+(?:at|@|with|for|in)\s+"
        
        for i, line in enumerate(lines):
            # Skip very short lines
            if len(line) < 10:
                continue
            
            if "Experience" in line:  # Section header
                continue
                
            dates = re.findall(date_pattern, line, re.IGNORECASE)
            if dates:
                # Split line into parts around the date
                parts = re.split(date_pattern, line)
                title_part = parts[0].strip()
                company_part = parts[-1].strip() if len(parts) > 2 else ""
                
                # Try to extract title and company
                if at_pattern in title_part:
                    title, company = title_part.split(at_pattern, 1)
                    experiences.append({
                        "title": title.strip(),
                        "company": company.strip(),
                        "dates": dates[0]
                    })
                else:
                    # Look ahead for company in next line
                    company = company_part or (lines[i+1] if i+1 < len(lines) else "")
                    experiences.append({
                        "title": title_part,
                        "company": company.strip(),
                        "dates": dates[0]
                    })
        """Extract structured work experience entries from text."""
        experiences = []
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        
        # Patterns for identifying experience entries
        date_pattern = r"(?:\d{4}[-–]\d{4}|\d{4}\s*[-–]\s*(?:present|current|now)|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})"
        title_pattern = r"\b(Senior|Lead|Principal|Staff|Software|Developer|Engineer|Manager|Director|Architect|Consultant)\b"
        
        current_entry = {}
        for line in lines:
            # Skip very short lines as they're unlikely to be complete entries
            if len(line) < 10:
                continue
                
            # Look for date ranges that typically start experience entries
            if re.search(date_pattern, line, re.IGNORECASE):
                # If we have a previous entry, save it
                if current_entry:
                    experiences.append(current_entry)
                current_entry = {"dates": re.search(date_pattern, line, re.IGNORECASE).group()}
                
                # Try to extract title and company from the same line
                if re.search(title_pattern, line):
                    # Split the line around the date to separate title/company
                    parts = re.split(date_pattern, line)
                    if len(parts) >= 2:
                        current_entry["title"] = parts[0].strip()
                        current_entry["company"] = parts[1].strip()
            
            # If we have a current entry but missing title/company
            elif current_entry:
                if "title" not in current_entry and re.search(title_pattern, line):
                    current_entry["title"] = line.strip()
                elif "company" not in current_entry and not re.search(date_pattern, line):
                    current_entry["company"] = line.strip()
                
                # Add description if we have the main entry details
                if "title" in current_entry and "company" in current_entry:
                    current_entry.setdefault("description", line.strip())
        
        # Add the last entry if we have one
        if current_entry:
            experiences.append(current_entry)
        
        # Clean and deduplicate entries
        clean_experiences = []
        seen = set()
        for exp in experiences:
            key = (exp.get("company", ""), exp.get("title", ""), exp.get("dates", ""))
            if key not in seen:
                seen.add(key)
                clean_experiences.append(exp)
        
        return clean_experiences[:10]  # Limit to top 10 most recent

    def extract_education(self, text: str) -> List[Dict[str, Optional[str]]]:
        """Extract structured education entries from text."""
        education = []
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        
        # Process education section
        in_education = False
        current_degree = None
        current_institution = None
        current_dates = None
        
        for line in lines:
            if "Education" in line:
                in_education = True
                continue
                
            if in_education and line:
                if "BS" in line or "BA" in line or "Computer Science" in line:
                    current_degree = line
                elif "University" in line or "," in line:
                    parts = line.split(",")
                    current_institution = parts[0].strip()
                    if len(parts) > 1:
                        current_dates = parts[1].strip()
                        
                    # Add complete entry
                    if current_degree and current_institution:
                        education.append({
                            "degree": current_degree,
                            "institution": current_institution,
                            "dates": current_dates
                        })
                        current_degree = current_institution = current_dates = None
                        
        return education
        """Extract structured education entries from text."""
        education = []
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        
        degree_pattern = r"(BS|BA|B\.Sc|MS|M\.Sc|PhD|MBA|Bachelor|Master|Doctor|Associate|Diploma|Certificate)"
        date_pattern = r"((?:19|20)\d{2}[-–]\d{4}|(?:19|20)\d{2}[-–](?:present|current|now))"
        university_pattern = r"(University|College|Institute|School)"
        at_pattern = r"\s+(?:at|@|with|from|in)\s+"
        
        for i, line in enumerate(lines):
            if len(line) < 10:
                continue
                
            if "Education" in line:  # Section header
                continue
            
            dates = re.findall(date_pattern, line, re.IGNORECASE)
            degree_match = re.search(degree_pattern, line, re.IGNORECASE)
            
            if degree_match or dates:
                # Extract degree and institution if line contains at/from/in
                if at_pattern in line:
                    parts = re.split(at_pattern, line, 1)
                    degree = parts[0].strip()
                    institution = parts[1].strip()
                    # Clean up date if it's in institution part
                    if dates:
                        institution = re.sub(date_pattern, "", institution).strip()
                else:
                    degree = line.strip()
                    # Try to get institution from next line if available
                    institution = lines[i+1] if i+1 < len(lines) else ""
                    
                education.append({
                    "degree": degree,
                    "institution": institution,
                    "dates": dates[0] if dates else ""
                })
        """Extract structured education entries from text."""
        education = []
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        
        # Enhanced patterns for education extraction
        degree_pattern = r"\b(BS|BA|B\.Sc|MS|M\.Sc|PhD|MBA|Bachelor|Master|Doctor|Associate|Diploma|Certificate)\b"
        date_pattern = r"(?:\d{4}[-–]\d{4}|\d{4})"
        institution_keywords = r"\b(University|College|Institute|School)\b"
        
        current_entry = {}
        for line in lines:
            if len(line) < 10:
                continue
                
            # Look for lines containing degree information
            if re.search(degree_pattern, line, re.IGNORECASE):
                # Save previous entry if exists
                if current_entry:
                    education.append(current_entry)
                current_entry = {"degree": line.strip()}
                
                # Try to extract date and institution from same line
                if re.search(date_pattern, line):
                    current_entry["dates"] = re.search(date_pattern, line).group()
                if re.search(institution_keywords, line, re.IGNORECASE):
                    # Try to extract institution name around the matched keyword
                    inst_match = re.search(fr".*?({institution_keywords}).*?(?={date_pattern}|\Z)", line, re.IGNORECASE)
                    if inst_match:
                        current_entry["institution"] = inst_match.group().strip()
            
            # If we have a current entry but missing information
            elif current_entry:
                if "dates" not in current_entry and re.search(date_pattern, line):
                    current_entry["dates"] = re.search(date_pattern, line).group()
                elif "institution" not in current_entry and re.search(institution_keywords, line, re.IGNORECASE):
                    current_entry["institution"] = line.strip()
        
        # Add the last entry if we have one
        if current_entry:
            education.append(current_entry)
        
        # Clean and deduplicate entries
        clean_education = []
        seen = set()
        for edu in education:
            key = (edu.get("degree", ""), edu.get("institution", ""), edu.get("dates", ""))
            if key not in seen:
                seen.add(key)
                clean_education.append(edu)
        
        return clean_education[:10]  # Limit to top 10 most recent

    def calculate_experience_years(self, text: str) -> int:
        pattern = r"(\d+)\s*(?:\+)?\s*years?\s+(?:of\s+)?experience"
        matches = re.findall(pattern, text.lower())
        if matches:
            years = [int(m) for m in matches if m.isdigit()]
            return max(years) if years else 0
        # Fallback: look for year ranges like 2018-2022
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
            # Extract text depending on file type
            if mimetype == "application/pdf":
                text = self.extract_text_from_pdf(filepath)
            elif mimetype.endswith("wordprocessingml.document") or filepath.lower().endswith('.docx'):
                text = self.extract_text_from_docx(filepath)
            else:
                raise FileParseError(f"Unsupported file type: {mimetype}")

            # Get basic NER enrichments first
            spacy_info = self._extract_with_spacy(text)
            
            # Build personal info section
            personal_info = {
                "name": spacy_info.get("name"),
                "email": self.extract_email(text),
                "phone": self.extract_phone(text),
                "location": None  # TODO: Add location extraction
            }

            # Extract structured experience and education
            experience_entries = self.extract_experience(text)
            education_entries = self.extract_education(text)

            # Calculate confidence based on completeness
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
                "skills": self.extract_skills(text),
                "experience": experience_entries,
                "education": education_entries,
                "experience_years": self.calculate_experience_years(text),
                "confidence_score": round(confidence_score, 2),
                "error": None
            }

            return parsed_data
            
        except FileParseError as e:
            # Known parsing errors
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
        # Try loading skills.json adjacent to this file
        base_dir = os.path.dirname(__file__)
        skills_file = os.path.join(base_dir, "skills.json")
        if os.path.exists(skills_file):
            try:
                with open(skills_file, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    if isinstance(data, list):
                        return data
            except Exception as e:
                logger.exception("Failed to load skills.json: %s", e)

        # Fallback hardcoded list
        return [
            "Python", "JavaScript", "TypeScript", "React", "Node.js", "FastAPI",
            "Django", "Flask", "SQL", "PostgreSQL", "MySQL", "MongoDB",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
            "Git", "CI/CD", "Jenkins", "CircleCI", "Data Science", "Machine Learning",
            "Pandas", "NumPy", "scikit-learn", "PyTorch", "TensorFlow", "NLP",
            "Docker", "Redis", "Kafka", "GraphQL", "REST", "HTML", "CSS"
        ]
