from fastapi import APIRouter, Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db
from app.core.security import decode_token
from app.models.jobs import Job
from app.models.candidate import Candidate
from app.models.applications import Application
from app.models.screening_results import ScreeningResult


router = APIRouter()


def extract_user_id(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    try:
        scheme, token = authorization.split()
        assert scheme.lower() == "bearer"
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_id


@router.get("/analytics/summary")
async def analytics_summary(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Return high-level analytics summary for dashboard."""
    extract_user_id(authorization)

    total_jobs = (await db.execute(select(func.count()).select_from(Job))).scalar() or 0
    total_candidates = (await db.execute(select(func.count()).select_from(Candidate))).scalar() or 0
    total_applications = (await db.execute(select(func.count()).select_from(Application))).scalar() or 0
    hired_count = (await db.execute(select(func.count()).select_from(Application).where(Application.status == "hired"))).scalar() or 0

    avg_match = (await db.execute(select(func.avg(ScreeningResult.overall_score)))).scalar()
    avg_match_score = float(avg_match) if avg_match is not None else 0.0

    return {
        "totalJobs": total_jobs,
        "totalCandidates": total_candidates,
        "totalApplications": total_applications,
        "hiredCount": hired_count,
        "avgMatchScore": round(avg_match_score * 100, 1) if avg_match_score <= 1 else round(avg_match_score, 1),
        # Placeholders for now; can be computed from timestamps later
        "conversionRate": 0.0,
        "timeToHire": 0,
    }


