from fastapi import APIRouter, HTTPException, status, Header, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.models.jobs import Job
from app.models.resume import Resume
from app.models.candidate import Candidate
from app.models.screening_results import ScreeningResult
from app.core.security import decode_token
from pydantic import BaseModel
from typing import Optional, List
import uuid
import logging
from app.services.embeddings import get_embedding, vector_store

logger = logging.getLogger(__name__)

router = APIRouter()


# ========== PYDANTIC SCHEMAS ==========

class MatchRequest(BaseModel):
    """Request schema for matching candidates to a job"""
    job_id: str
    candidate_id: str
    resume_id: str


class MatchResult(BaseModel):
    """Individual candidate match result"""
    candidate_id: str
    candidate_name: str
    resume_filename: str
    overall_score: float
    skill_match_score: float
    experience_score: float
    education_score: float
    reasoning: str


# ========== HELPER FUNCTION ==========

def extract_user_id(authorization: str) -> str:
    """Extract user_id from Bearer token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise ValueError
        token = parts[1]
    except:
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user_id


# ========== MATCHING ALGORITHM ==========

def calculate_skill_match(job_requirements: str, resume_skills: List[str]) -> float:
    """
    Calculate skill match score between job requirements and resume skills.
    
    Returns score between 0 and 1.
    """
    if not resume_skills:
        return 0.0
    
    # Convert to lowercase for comparison
    requirements_lower = job_requirements.lower()
    skills_lower = [s.lower() for s in resume_skills]
    
    # Count matching skills
    matches = 0
    for skill in skills_lower:
        if skill in requirements_lower:
            matches += 1
    
    # Calculate percentage match
    score = min(1.0, matches / max(len(skills_lower), 1))
    return round(score, 2)


def calculate_experience_score(job_requirements: str, resume_experience_years: Optional[int]) -> float:
    """
    Calculate experience match score.
    
    Returns score between 0 and 1.
    """
    if not resume_experience_years:
        return 0.5  # Neutral score if not specified
    
    # Look for experience requirements in job description
    # Very basic parsing - in production, use NLP
    if "senior" in job_requirements.lower():
        # Senior role expects 5+ years
        experience_score = min(1.0, resume_experience_years / 5)
    elif "junior" in job_requirements.lower():
        # Junior role expects 0-2 years
        experience_score = 1.0 if resume_experience_years <= 2 else 0.7
    else:
        # Regular role - any experience counts
        experience_score = min(1.0, resume_experience_years / 3)
    
    return round(experience_score, 2)


def calculate_education_score(resume_education_level: Optional[str]) -> float:
    """
    Calculate education match score.
    
    Returns score between 0 and 1.
    """
    if not resume_education_level:
        return 0.5  # Neutral if not specified
    
    education_level = resume_education_level.lower()
    
    # Score higher education levels
    if "phd" in education_level or "doctorate" in education_level:
        return 1.0
    elif "master" in education_level:
        return 0.9
    elif "bachelor" in education_level or "b.s." in education_level or "b.a." in education_level:
        return 0.8
    elif "associate" in education_level or "diploma" in education_level:
        return 0.7
    else:
        return 0.5  # Default for unknown education


def calculate_overall_score(
    skill_match: float,
    experience_score: float,
    education_score: float
) -> float:
    """
    Calculate overall match score using weighted average.
    
    Weights:
    - Skills: 50%
    - Experience: 30%
    - Education: 20%
    """
    overall = (skill_match * 0.5) + (experience_score * 0.3) + (education_score * 0.2)
    return round(overall, 2)


# ========== ENDPOINTS ==========

@router.post("/match", status_code=status.HTTP_201_CREATED)
async def match_candidate_to_job(
    request: MatchRequest,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Match a candidate to a job and calculate compatibility scores.
    
    This endpoint:
    1. Retrieves job requirements
    2. Retrieves candidate resume data
    3. Calculates match scores
    4. Stores results in database
    5. Returns scores and reasoning
    """
    user_id = extract_user_id(authorization)
    
    # Validate UUIDs
    try:
        job_id = uuid.UUID(request.job_id)
        candidate_id = uuid.UUID(request.candidate_id)
        resume_id = uuid.UUID(request.resume_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format (must be UUID)")
    
    # Get job
    job_result = await db.execute(
        select(Job).where(Job.id == job_id)
    )
    job = job_result.scalars().first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get candidate
    candidate_result = await db.execute(
        select(Candidate).where(Candidate.id == candidate_id)
    )
    candidate = candidate_result.scalars().first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Get resume
    resume_result = await db.execute(
        select(Resume).where(Resume.id == resume_id)
    )
    resume = resume_result.scalars().first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Calculate scores
    # Keyword skill match
    skill_match_score = calculate_skill_match(job.requirements, resume.skills or [])
    # Vector similarity between job text and resume text/skills
    try:
        job_text = f"{job.title}\n{job.description}\n{job.requirements}"
        job_vec = get_embedding(job_text[:5000])
        # Query resumes namespace for this resume id to get a comparable score
        results = vector_store.query("resumes", job_vec, top_k=1, filter={"filename": resume.filename})
        vector_sim = results[0]["score"] if results else 0.0
        # Hybridize skill match with vector sim (average)
        skill_match_score = round((skill_match_score + float(vector_sim)) / 2, 2)
    except Exception:
        pass
    experience_score = calculate_experience_score(job.requirements, resume.experience_years)
    education_score = calculate_education_score(resume.education_level)
    overall_score = calculate_overall_score(skill_match_score, experience_score, education_score)
    
    # Generate reasoning (with simple RAG: include top resume snippet if available)
    reasoning = f"Skill match: {skill_match_score*100:.0f}%, Experience: {experience_score*100:.0f}%, Education: {education_score*100:.0f}%"
    try:
        # Use vector store to fetch top similar resumes and attach a small snippet from candidate resume parsed data if present
        # This is a lightweight RAG-style reasoning without LLM calls
        from app.models.resume import Resume as ResumeModel  # local import to avoid cycles
        resume_detail = resume
        # Append first 200 chars of raw_text to reasoning if present
        if getattr(resume_detail, 'raw_text', None):
            snippet = (resume_detail.raw_text or '')[:200]
            if snippet:
                reasoning += f"\nSnippet: {snippet}"
    except Exception:
        pass
    
    # Store in database
    screening_result = ScreeningResult(
        id=uuid.uuid4(),
        job_id=job_id,
        candidate_id=candidate_id,
        resume_id=resume_id,
        overall_score=overall_score,
        skill_match_score=skill_match_score,
        experience_score=experience_score,
        education_score=education_score,
        detailed_analysis={
            "skills": resume.skills or [],
            "experience_years": resume.experience_years,
            "education_level": resume.education_level,
            "reasoning": reasoning
        }
    )
    
    db.add(screening_result)
    await db.commit()
    await db.refresh(screening_result)
    
    logger.info(f"Match created: job={job_id}, candidate={candidate_id}, score={overall_score}")
    
    return {
        "message": "Candidate matched to job",
        "screening_result_id": str(screening_result.id),
        "job_id": str(job.id),
        "job_title": job.title,
        "candidate_id": str(candidate.id),
        "candidate_name": candidate.name,
        "resume_filename": resume.filename,
        "overall_score": overall_score,
        "skill_match_score": skill_match_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "reasoning": reasoning
    }


@router.get("/results/{job_id}")
async def get_match_results(
    job_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    min_score: Optional[float] = Query(None, ge=0, le=1, description="Filter by minimum score"),
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all match results for a job, sorted by score (highest first).
    
    Query Parameters:
    - skip: Number of records to skip
    - limit: Number of records to return
    - min_score: Only return matches above this score (0-1)
    """
    user_id = extract_user_id(authorization)
    
    # Validate UUID
    try:
        jid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    # Get job
    job_result = await db.execute(
        select(Job).where(Job.id == jid)
    )
    job = job_result.scalars().first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Build query
    query = select(ScreeningResult).where(ScreeningResult.job_id == jid)
    
    # Filter by minimum score if provided
    if min_score is not None:
        query = query.where(ScreeningResult.overall_score >= min_score)
    
    # Order by score descending (best matches first)
    query = query.order_by(desc(ScreeningResult.overall_score))
    
    # Add pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    screening_results = result.scalars().all()
    
    # Get candidate and resume details for each result
    results_with_details = []
    for sr in screening_results:
        # Get candidate
        candidate_result = await db.execute(
            select(Candidate).where(Candidate.id == sr.candidate_id)
        )
        candidate = candidate_result.scalars().first()
        
        # Get resume
        resume_result = await db.execute(
            select(Resume).where(Resume.id == sr.resume_id)
        )
        resume = resume_result.scalars().first()
        
        if candidate and resume:
            results_with_details.append({
                "screening_result_id": str(sr.id),
                "candidate_id": str(sr.candidate_id),
                "candidate_name": candidate.name,
                "resume_id": str(sr.resume_id),
                "resume_filename": resume.filename,
                "overall_score": sr.overall_score,
                "skill_match_score": sr.skill_match_score,
                "experience_score": sr.experience_score,
                "education_score": sr.education_score,
                "created_at": sr.created_at.isoformat() if sr.created_at else None
            })
    
    return {
        "job_id": str(job.id),
        "job_title": job.title,
        "total_matches": len(results_with_details),
        "results": results_with_details,
        "skip": skip,
        "limit": limit,
        "average_score": round(sum(r["overall_score"] for r in results_with_details) / max(len(results_with_details), 1), 2) if results_with_details else 0
    }
