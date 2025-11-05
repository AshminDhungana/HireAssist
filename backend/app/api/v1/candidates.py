from fastapi import APIRouter, HTTPException, status, Header, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.core.security import decode_token
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# ========== SCHEMAS ==========

class CandidateCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None


class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None


# ========== HELPERS ==========

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


# ========== ENDPOINTS ==========

@router.post("/create-profile", status_code=status.HTTP_201_CREATED)
async def create_candidate_profile(
    data: CandidateCreate,
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Create candidate profile for authenticated user"""
    user_id = extract_user_id(authorization)
    
    # Check if already exists
    result = await db.execute(
        select(Candidate).where(Candidate.user_id == user_id)
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Candidate profile already exists")
    
    # Create
    candidate = Candidate(
        id=uuid.uuid4(),
        user_id=user_id,
        name=data.name,
        email=data.email,
        phone=data.phone,
        location=data.location,
        summary=data.summary
    )
    
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)
    
    logger.info(f"Candidate created: {candidate.id}")
    
    return {
        "message": "Candidate profile created",
        "candidate_id": str(candidate.id)
    }


@router.get("/me")
async def get_my_profile(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's candidate profile with resumes"""
    user_id = extract_user_id(authorization)
    
    # Get candidate
    result = await db.execute(
        select(Candidate).where(Candidate.user_id == user_id)
    )
    candidate = result.scalars().first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    
    # Get resumes
    resumes = await db.execute(
        select(Resume)
        .where(Resume.candidate_id == candidate.id)
        .order_by(desc(Resume.created_at))
    )
    resumes = resumes.scalars().all()
    
    return {
        "candidate": {
            "id": str(candidate.id),
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "location": candidate.location,
            "summary": candidate.summary
        },
        "resumes": [
            {
                "id": str(r.id),
                "filename": r.filename,
                "skills": r.skills or [],
                "experience_years": r.experience_years,
                "education_level": r.education_level,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in resumes
        ],
        "resume_count": len(resumes)
    }


@router.put("/update-profile")
async def update_profile(
    data: CandidateUpdate,
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's candidate profile"""
    user_id = extract_user_id(authorization)
    
    result = await db.execute(
        select(Candidate).where(Candidate.user_id == user_id)
    )
    candidate = result.scalars().first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    
    # Update provided fields
    for field, value in data.dict(exclude_unset=True).items():
        setattr(candidate, field, value)
    
    db.add(candidate)
    await db.commit()
    
    return {"message": "Profile updated"}


@router.get("/list")
async def list_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """List all candidates"""
    user_id = extract_user_id(authorization)
    
    result = await db.execute(
        select(Candidate)
        .order_by(desc(Candidate.created_at))
        .offset(skip)
        .limit(limit)
    )
    candidates = result.scalars().all()
    
    return {
        "candidates": [
            {
                "id": str(c.id),
                "name": c.name,
                "email": c.email,
                "location": c.location,
                "phone": c.phone
            }
            for c in candidates
        ],
        "total": len(candidates)
    }


@router.get("/{candidate_id}")
async def get_candidate(
    candidate_id: str,
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Get candidate details"""
    user_id = extract_user_id(authorization)
    
    try:
        cid = uuid.UUID(candidate_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid candidate ID")
    
    result = await db.execute(
        select(Candidate).where(Candidate.id == cid)
    )
    candidate = result.scalars().first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return {
        "id": str(candidate.id),
        "name": candidate.name,
        "email": candidate.email,
        "phone": candidate.phone,
        "location": candidate.location,
        "summary": candidate.summary
    }


@router.delete("/delete-profile")
async def delete_profile(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Delete current user's candidate profile"""
    user_id = extract_user_id(authorization)
    
    result = await db.execute(
        select(Candidate).where(Candidate.user_id == user_id)
    )
    candidate = result.scalars().first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    
    await db.delete(candidate)
    await db.commit()
    
    logger.info(f"Candidate deleted: {candidate.id}")
    
    return {"message": "Profile deleted"}