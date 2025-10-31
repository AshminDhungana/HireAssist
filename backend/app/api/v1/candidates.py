from fastapi import APIRouter, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from fastapi import Depends
from app.models.candidate import Candidate
from app.core.security import decode_token
import uuid


router = APIRouter()


class CandidateCreate:
    def __init__(self, name: str, email: str, phone: str = None, location: str = None, summary: str = None):
        self.name = name
        self.email = email
        self.phone = phone
        self.location = location
        self.summary = summary


@router.post("/create-profile")
async def create_candidate_profile(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Create candidate profile for authenticated user.
    
    **Header required:**
    - authorization: "Bearer <your_token>"
    """
    # ===== AUTHENTICATION =====
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    
    try:
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise ValueError
        token = parts[1]
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Check if candidate already exists
    result = await db.execute(
        select(Candidate).where(Candidate.user_id == user_id)
    )
    existing = result.scalars().first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate profile already exists"
        )
    
    # Create candidate profile
    candidate = Candidate(
        id=uuid.uuid4(),
        user_id=user_id,
        name="",  # Will be updated by user
        email="",
    )
    
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)
    
    return {
        "message": "Candidate profile created successfully",
        "candidate_id": str(candidate.id),
        "user_id": str(candidate.user_id)
    }
