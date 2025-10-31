"""Comprehensive skills database tests."""
import pytest
import json
import os
from app.services.resumeparser import ResumeParser


@pytest.fixture
def parser():
    """Create a ResumeParser instance."""
    return ResumeParser()


@pytest.fixture
def skills_db():
    """Load skills database."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'skills_database.json')
    with open(db_path, 'r') as f:
        return json.load(f)


class TestSkillsDatabase:
    """Test skills database structure and content."""
    
    def test_database_exists(self, skills_db):
        """Verify skills database loads and is not empty."""
        assert skills_db is not None
        assert isinstance(skills_db, dict)
        assert len(skills_db) > 0
    
    def test_database_has_required_categories(self, skills_db):
        """Verify all required skill categories exist."""
        required_categories = {
            "programming_languages",
            "frontend_frameworks",
            "backend_frameworks",
            "databases",
            "cloud_platforms",
            "devops_tools",
            "data_science",
            "tools_and_platforms"
        }
        actual_categories = set(skills_db.keys())
        missing = required_categories - actual_categories
        assert len(missing) == 0, f"Missing categories: {missing}"
    
    def test_each_category_has_skills(self, skills_db):
        """Verify each category contains skill entries."""
        for category, skills in skills_db.items():
            assert isinstance(skills, list), f"{category} should be a list"
            assert len(skills) > 0, f"{category} should have at least one skill"
            
            # Verify all skills are strings
            for skill in skills:
                assert isinstance(skill, str), f"Skill in {category} should be string: {skill}"
    
    def test_total_skills_count(self, skills_db):
        """Verify database has sufficient number of total skills."""
        total = sum(len(skills) for skills in skills_db.values())
        assert total >= 150, f"Database should have 150+ skills, has {total}"
    
    def test_no_duplicate_skills_in_category(self, skills_db):
        """Verify no duplicate skills within each category."""
        for category, skills in skills_db.items():
            unique_skills = set(skill.lower() for skill in skills)
            assert len(unique_skills) == len(skills), f"Duplicates found in {category}"


class TestSkillExtraction:
    """Test skill extraction from resume text."""
    
    def test_extract_programming_languages(self, parser):
        """Test extracting programming language skills."""
        text = "Experienced with Python, JavaScript, and Java programming"
        skills = parser.extract_skills(text)
        
        # At least one programming language should be found
        assert len(skills) > 0, "Should extract at least one skill"
        # Verify Python is found
        assert any('python' in s.lower() for s in skills), "Python not found in skills"
    
    def test_extract_frameworks(self, parser):
        """Test extracting framework skills."""
        text = "Built web applications with React, Django, and FastAPI frameworks"
        skills = parser.extract_skills(text)
        
        # Should extract multiple frameworks
        assert len(skills) >= 2, f"Should find at least 2 frameworks, found {len(skills)}"
    
    def test_extract_databases(self, parser):
        """Test extracting database skills."""
        text = "Database experience with PostgreSQL, MongoDB, and Redis"
        skills = parser.extract_skills(text)
        
        assert len(skills) >= 2, f"Should find at least 2 databases, found {len(skills)}"
    
    def test_extract_cloud_tools(self, parser):
        """Test extracting cloud and DevOps skills."""
        text = "Deployed using AWS, Docker, and Kubernetes on cloud infrastructure"
        skills = parser.extract_skills(text)
        
        assert len(skills) >= 2, f"Should find cloud/DevOps skills, found {len(skills)}"
    
    def test_normalize_skill_abbreviations(self, parser):
        """Test normalization of abbreviated skill names."""
        text = "Experience with py, js, ts, and sql"
        skills = parser.extract_skills(text)
        
        # Should normalize abbreviated forms
        skills_lower = [s.lower() for s in skills]
        has_python = any('python' in s for s in skills_lower)
        has_javascript = any('javascript' in s for s in skills_lower)
        
        # At least one should be normalized
        assert has_python or has_javascript, "Should normalize at least one abbreviation"
    
    def test_no_false_positives_common_words(self, parser):
        """Verify common words are not extracted as skills."""
        text = "I worked with my team to solve problems and deliver quality solutions effectively"
        skills = parser.extract_skills(text)
        
        # Common non-skills
        false_positive_words = {'work', 'team', 'solve', 'problems', 'deliver', 'quality', 'solutions', 'effectively'}
        
        for skill in skills:
            skill_lower = skill.lower()
            assert skill_lower not in false_positive_words, f"'{skill}' should not be extracted as skill"
    
    def test_extract_from_empty_text(self, parser):
        """Test that empty text returns no skills."""
        skills = parser.extract_skills("")
        assert skills == [], "Empty text should return no skills"
    
    def test_extract_from_whitespace_only(self, parser):
        """Test that whitespace-only text returns no skills."""
        skills = parser.extract_skills("   \n  \t  ")
        assert len(skills) == 0, "Whitespace-only text should return no skills"


class TestSkillIntegration:
    """Integration tests with realistic resume scenarios."""
    
    def test_full_resume_skill_extraction(self, parser):
        """Test skill extraction from realistic full resume."""
        resume = """
        JOHN DOE
        john.doe@example.com | (555) 123-4567
        
        PROFESSIONAL SUMMARY
        Senior Software Engineer with 5+ years experience building scalable applications
        
        TECHNICAL SKILLS
        Languages: Python, JavaScript, TypeScript, Java
        Frontend: React, Vue.js, Angular, Tailwind CSS
        Backend: FastAPI, Django, Node.js, Express
        Databases: PostgreSQL, MongoDB, Redis
        Cloud & DevOps: AWS, Docker, Kubernetes, GitHub Actions
        
        PROFESSIONAL EXPERIENCE
        Senior Developer at TechCorp (2020-Present)
        - Led development of microservices using FastAPI and Python
        - Deployed containerized applications on AWS using Docker and Kubernetes
        - Built responsive frontends with React and TypeScript
        - Managed PostgreSQL and MongoDB databases
        - Implemented CI/CD pipelines with GitHub Actions
        
        Software Developer at StartupXYZ (2018-2020)
        - Developed full-stack applications with Node.js and React
        - Worked with SQL and NoSQL databases
        - Deployed applications on cloud platforms
        """
        
        skills = parser.extract_skills(resume)
        
        # Should extract substantial number of skills from full resume
        assert len(skills) >= 10, f"Should find 10+ skills, found {len(skills)}: {skills}"
        
        # Verify diverse skill categories are represented
        skills_lower = [s.lower() for s in skills]
        
        # Check for programming languages
        has_programming_lang = any(
            lang in ' '.join(skills_lower) 
            for lang in ['python', 'javascript', 'java', 'typescript']
        )
        assert has_programming_lang, "Should find programming languages"
        
        # Check for frameworks
        has_framework = any(
            fw in ' '.join(skills_lower) 
            for fw in ['fastapi', 'django', 'react', 'express', 'node']
        )
        assert has_framework, "Should find frameworks"
        
        # Check for databases
        has_database = any(
            db in ' '.join(skills_lower) 
            for db in ['postgresql', 'postgres', 'mongodb', 'redis']
        )
        assert has_database, "Should find databases"
        
        # Check for DevOps/Cloud tools
        has_devops = any(
            tool in ' '.join(skills_lower) 
            for tool in ['docker', 'kubernetes', 'aws', 'github']
        )
        assert has_devops, "Should find DevOps/Cloud tools"
    
    def test_skill_extraction_from_experience_section(self, parser):
        """Test extracting skills mentioned in experience section."""
        experience = """
        Senior Developer at Tech Company (2020-2023)
        Led Python and FastAPI backend development team
        Architected microservices deployed on AWS using Docker
        Implemented machine learning models with TensorFlow
        Managed PostgreSQL and Redis databases
        """
        
        skills = parser.extract_skills(experience)
        
        # Should extract multiple technical skills
        assert len(skills) >= 5, f"Should find 5+ skills from experience, found {len(skills)}"
    
    def test_skill_deduplication(self, parser):
        """Test that same skill mentioned multiple times is not duplicated."""
        text = "Python Python python Python expertise in Python programming with Python"
        skills = parser.extract_skills(text)
        
        # Count Python occurrences
        python_count = sum(1 for s in skills if 'python' in s.lower())
        
        # Should only appear once (or normalized to single entry)
        assert python_count <= 1, f"Python should appear only once, appears {python_count} times"


class TestSkillNormalization:
    """Test skill name normalization and standardization."""
    
    def test_case_insensitive_extraction(self, parser):
        """Test that skills are extracted regardless of case."""
        test_cases = [
            "PYTHON",
            "python",
            "Python",
            "PyThOn"
        ]
        
        for variant in test_cases:
            text = f"Experience with {variant} programming"
            skills = parser.extract_skills(text)
            
            # Should find the skill regardless of case
            has_python = any('python' in s.lower() for s in skills)
            assert has_python, f"Failed to find Python from '{variant}' variant"
    
    def test_multiword_skill_detection(self, parser):
        """Test detection of multi-word skills like 'Machine Learning'."""
        text = "Expertise in machine learning and deep learning algorithms"
        skills = parser.extract_skills(text)
        
        # Should handle multi-word phrases
        assert len(skills) >= 1, "Should detect multi-word skills"
