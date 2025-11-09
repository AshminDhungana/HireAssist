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
from asyncpg import Range

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

class JobResponse(BaseModel):
    """Schema for job response"""
    id: str
    title: str
    description: str
    requirements: str
    location: str
    salary_min: Optional[int]
    salary_max: Optional[int]
    status: str
    created_at: str
    
    class Config:
        from_attributes = True

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
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Create a new job posting"""
    user_id = extract_user_id(authorization)

    salary_range = None
    if job_data.salary_min is not None or job_data.salary_max is not None:
        salary_range = Range(
            lower=job_data.salary_min,
            upper=job_data.salary_max,
            empty=False
        )

    job = Job(
        id=uuid.uuid4(),
        title=job_data.title,
        description=job_data.description,
        requirements=job_data.requirements,
        location=job_data.location,
        salary_range=salary_range,
        status="active",
        created_by=uuid.UUID(user_id)
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

    logger.info(f"Job created: {job.id}")

    try:
        job_text = f"{job.title} {job.description} {job.requirements}"
        embedding = await get_embedding(job_text)
        await vector_store.upsert(
            vectors=[(str(job.id), embedding, {"type": "job"})]
        )
    except Exception as e:
        logger.warning(f"Failed to create embedding for job {job.id}: {e}")

    return {
        "success": True,
        "job_id": str(job.id),
        "message": "Job created successfully"
    }

# ✅ NEW ENDPOINT: List all jobs
@router.get("/list")
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Get all active jobs with pagination"""
    user_id = extract_user_id(authorization)

    try:
        # Query all active jobs
        result = await db.execute(
            select(Job)
            .where(Job.status == "active")
            .order_by(desc(Job.created_at))
            .offset(skip)
            .limit(limit)
        )
        
        jobs = result.scalars().all()
        
        # Format response
        job_list = []
        for job in jobs:
            # Extract salary range
            salary_min = None
            salary_max = None
            if job.salary_range:
                salary_min = job.salary_range.lower
                salary_max = job.salary_range.upper
            
            job_list.append({
                "id": str(job.id),
                "title": job.title,
                "description": job.description,
                "requirements": job.requirements,
                "location": job.location,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "status": job.status,
                "created_at": job.created_at.isoformat() if job.created_at else None
            })
        
        return {
            "success": True,
            "jobs": job_list,
            "total": len(job_list)
        }
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")

# ✅ NEW ENDPOINT: Get single job
@router.get("/{job_id}")
async def get_job(
    job_id: str,
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific job by ID"""
    user_id = extract_user_id(authorization)

    try:
        result = await db.execute(
            select(Job).where(Job.id == uuid.UUID(job_id))
        )
        job = result.scalars().first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        salary_min = None
        salary_max = None
        if job.salary_range:
            salary_min = job.salary_range.lower
            salary_max = job.salary_range.upper
        
        return {
            "success": True,
            "job": {
                "id": str(job.id),
                "title": job.title,
                "description": job.description,
                "requirements": job.requirements,
                "location": job.location,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "status": job.status,
                "created_at": job.created_at.isoformat() if job.created_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job: {str(e)}")
