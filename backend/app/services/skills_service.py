import json
import os
from typing import List, Set
from difflib import SequenceMatcher

class SkillsDatabase:
    def __init__(self):
        self.skills = self._load_skills()
        self.skills_lower = {s.lower(): s for s in self.skills}
    
    def _load_skills(self) -> List[str]:
        """Load skills from skills.json"""
        skills_path = os.path.join(
            os.path.dirname(__file__),
            "skills.json"
        )
        
        try:
            with open(skills_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else data.get('skills', [])
        except Exception as e:
            print(f"Error loading skills: {e}")
            return []
    
    def get_all_skills(self) -> List[str]:
        """Return all available skills"""
        return sorted(self.skills)
    
    def search_skills(self, query: str, limit: int = 10) -> List[str]:
        """Search skills by name"""
        query_lower = query.lower()
        results = [
            skill for skill in self.skills
            if query_lower in skill.lower()
        ]
        return sorted(results)[:limit]
    
    def normalize_skill(self, skill: str) -> str:
        """Normalize skill name to match database"""
        if not skill:
            return ""
        
        skill_lower = skill.lower().strip()
        
        # Exact match
        if skill_lower in self.skills_lower:
            return self.skills_lower[skill_lower]
        
        # Fuzzy match (similarity > 80%)
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

# Create singleton instance
skills_db = SkillsDatabase()
