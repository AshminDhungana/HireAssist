from fastapi import APIRouter, HTTPException, Query
from app.services.skills_service import skills_db

router = APIRouter()

@router.get("/available")
async def get_available_skills():
    """Get all available skills"""
    skills = skills_db.get_all_skills()
    return {
        "total": len(skills),
        "skills": skills
    }

@router.get("/search")
async def search_skills(query: str = Query(..., min_length=1, max_length=100)):
    """Search skills by name"""
    if not query or len(query.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    results = skills_db.search_skills(query)
    return {
        "query": query,
        "total": len(results),
        "results": results
    }

@router.post("/normalize")
async def normalize_skills(skills: list[str]):
    """Normalize skills against database"""
    standardized = skills_db.standardize_skills(skills)
    return {
        "input": skills,
        "standardized": standardized
    }

@router.get("/categories")
async def get_skill_categories():
    """Get skills grouped by category"""
    categories = {
        "Frontend": ["React", "Vue", "Angular", "TypeScript", "HTML", "CSS", "Tailwind"],
        "Backend": ["Python", "JavaScript", "Java", "Go", "Rust", "FastAPI", "Django"],
        "Database": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch"],
        "DevOps": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform", "Jenkins"],
        "AI/ML": ["Python", "TensorFlow", "PyTorch", "scikit-learn", "spaCy", "Transformers"],
        "Mobile": ["React Native", "Flutter", "Swift", "Kotlin", "iOS", "Android"],
    }
    return categories

