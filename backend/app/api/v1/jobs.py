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
    """
    Create a new job posting.

    Required:
    - Authorization header with Bearer token
    - Request body with job details
    """
    user_id = extract_user_id(authorization)

    # Convert salary min/max to PostgreSQL Range object (CORRECT WAY)
    salary_range = None
    if job_data.salary_min is not None or job_data.salary_max is not None:
        # Use Range object for INT4RANGE - this is what PostgreSQL expects!
        salary_range = Range(
            lower=job_data.salary_min,
            upper=job_data.salary_max,
            empty=False
        )

    # Create job
    job = Job(
        id=uuid.uuid4(),
        title=job_data.title,
        description=job_data.description,
        requirements=job_data.requirements,
        location=job_data.location,
        salary_range=salary_range,  # ← Use Range object!
        status="active",
        created_by=uuid.UUID(user_id)
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

    logger.info(f"Job created: {job.id}")

    # Upsert job embedding for vector matching
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
