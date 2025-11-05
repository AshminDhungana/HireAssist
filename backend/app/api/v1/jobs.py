from fastapi import APIRouter, HTTPException, status, Header, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.core.database import get_db
from app.models.jobs import Job
from app.models.users import User
from app.core.security import decode_token
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
import logging
from app.services.embeddings import get_embedding, vector_store

logger = logging.getLogger(__name__)

router = APIRouter()


# ========== PYDANTIC SCHEMAS ==========

class JobCreate(BaseModel):
    """Schema for creating a job posting"""
    title: str
    description: str
    requirements: str
    location: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None


class JobUpdate(BaseModel):
    """Schema for updating a job posting"""
    title: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None


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


# ========== ENDPOINTS ==========

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new job posting.
    
    Required:
    - Authorization header with Bearer token
    - Request body with job details
    """
    user_id = extract_user_id(authorization)
    
    # Create job
    job = Job(
        id=uuid.uuid4(),
        title=job_data.title,
        description=job_data.description,
        requirements=job_data.requirements,
        location=job_data.location,
        salary_min=job_data.salary_min,
        salary_max=job_data.salary_max,
        status="active",
        created_by=uuid.UUID(user_id)
    )
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    logger.info(f"Job created: {job.id}")

    # Upsert job embedding for vector matching
    try:
        text = f"{job.title}\n{job.description}\n{job.requirements}"
        emb = get_embedding(text[:5000])
        vector_store.upsert("jobs", [(str(job.id), emb, {"title": job.title})])
    except Exception:
        logger.warning("Failed to upsert job embedding")
    
    return {
        "message": "Job posted successfully",
        "job_id": str(job.id),
        "title": job.title,
        "location": job.location
    }


@router.get("/list")
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, description="Filter by status (active, closed)"),
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    List all job postings with pagination.
    
    Query Parameters:
    - skip: Number of records to skip
    - limit: Number of records to return (max 100)
    - status_filter: Filter by job status (optional)
    """
    user_id = extract_user_id(authorization)
    
    # Build query
    query = select(Job).order_by(desc(Job.created_at))
    
    # Filter by status if provided
    if status_filter:
        query = query.where(Job.status == status_filter)
    else:
        # Default: show only active jobs
        query = query.where(Job.status == "active")
    
    # Add pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return {
        "jobs": [
            {
                "id": str(j.id),
                "title": j.title,
                "description": j.description,
                "requirements": j.requirements,
                "location": j.location,
                "salary_min": j.salary_min,
                "salary_max": j.salary_max,
                "status": j.status,
                "created_at": j.created_at.isoformat() if j.created_at else None
            }
            for j in jobs
        ],
        "total": len(jobs),
        "skip": skip,
        "limit": limit
    }


@router.get("/{job_id}")
async def get_job_details(
    job_id: str,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific job.
    
    Path Parameter:
    - job_id: UUID of the job
    """
    user_id = extract_user_id(authorization)
    
    # Validate UUID
    try:
        jid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    result = await db.execute(
        select(Job).where(Job.id == jid)
    )
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "id": str(job.id),
        "title": job.title,
        "description": job.description,
        "requirements": job.requirements,
        "location": job.location,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "status": job.status,
        "created_by": str(job.created_by),
        "created_at": job.created_at.isoformat() if job.created_at else None
    }


@router.put("/{job_id}")
async def update_job(
    job_id: str,
    job_data: JobUpdate,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a job posting.
    
    Only the creator can update.
    All fields are optional.
    """
    user_id = extract_user_id(authorization)
    
    # Validate UUID
    try:
        jid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    result = await db.execute(
        select(Job).where(Job.id == jid)
    )
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check ownership (only creator can update)
    if str(job.created_by) != user_id:
        raise HTTPException(status_code=403, detail="You can only update your own jobs")
    
    # Update provided fields
    for field, value in job_data.dict(exclude_unset=True).items():
        setattr(job, field, value)
    
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    logger.info(f"Job updated: {job.id}")
    
    return {
        "message": "Job updated successfully",
        "job_id": str(job.id)
    }


@router.delete("/{job_id}")
async def delete_job(
    job_id: str,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a job posting.
    
    Only the creator can delete.
    """
    user_id = extract_user_id(authorization)
    
    # Validate UUID
    try:
        jid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    result = await db.execute(
        select(Job).where(Job.id == jid)
    )
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check ownership (only creator can delete)
    if str(job.created_by) != user_id:
        raise HTTPException(status_code=403, detail="You can only delete your own jobs")
    
    job_title = job.title
    
    await db.delete(job)
    await db.commit()
    
    logger.info(f"Job deleted: {job_id}")
    
    return {
        "message": "Job deleted successfully",
        "deleted_job_id": job_id,
        "title": job_title
    }
