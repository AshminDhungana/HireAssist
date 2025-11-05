from fastapi import APIRouter, Header, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.database import get_db
from app.core.security import decode_token
from app.models.resume import Resume
from app.models.jobs import Job
from app.models.candidate import Candidate
from app.services.task_queue import task_queue
from app.services.resumeparser import ResumeParser, FileParseError
from app.api.v1.matching import (
    calculate_skill_match,
    calculate_experience_score,
    calculate_education_score,
    calculate_overall_score,
)
from app.models.screening_results import ScreeningResult


router = APIRouter()


def require_auth(authorization: str) -> str:
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


@router.post("/tasks/parse-resume/{resume_id}")
async def enqueue_parse_resume(resume_id: str, authorization: str = Header(None)):
    require_auth(authorization)
    try:
        uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid resume id")
    task_id = task_queue.enqueue("parse_resume", {"resume_id": resume_id})
    return {"task_id": task_id, "status": "queued"}


class MatchTask(BaseModel):
    job_id: str
    candidate_id: str
    resume_id: str


@router.post("/tasks/match")
async def enqueue_match(task: MatchTask, authorization: str = Header(None)):
    require_auth(authorization)
    for fid in (task.job_id, task.candidate_id, task.resume_id):
        try:
            uuid.UUID(fid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid id format")
    task_id = task_queue.enqueue("match_candidate", task.model_dump())
    return {"task_id": task_id, "status": "queued"}


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str, authorization: str = Header(None)):
    require_auth(authorization)
    status = task_queue.get_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="Task not found")
    return status


# Register handlers once (import side-effect in main lifespan)
def _register_handlers():
    from app.services.embeddings import get_embedding, vector_store
    from app.core.database import async_session

    async def handle_parse(payload):
        rid = uuid.UUID(payload["resume_id"])
        async with async_session() as session:
            res = await session.execute(select(Resume).where(Resume.id == rid))
            resume = res.scalars().first()
            if not resume:
                raise RuntimeError("Resume not found")
            parser = ResumeParser()
            # Detect mimetype by filename
            fname = (resume.filename or "").lower()
            if fname.endswith('.pdf'):
                mimetype = 'application/pdf'
            elif fname.endswith('.docx'):
                mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            else:
                mimetype = 'application/octet-stream'
            parsed = parser.parse_resume(resume.file_path, mimetype)
            resume.parsed_data = parsed
            resume.raw_text = parsed.get('raw_text')
            resume.skills = parsed.get('skills') or []
            resume.experience_years = parsed.get('experience_years')
            # Simple education level extraction
            edu = parsed.get('education') or []
            resume.education_level = (edu[0].get('degree') if edu and isinstance(edu[0], dict) else None)
            session.add(resume)
            await session.commit()
            # Update embedding
            emb_text = (resume.raw_text or '') + '\n' + ' '.join(resume.skills or [])
            vec = get_embedding(emb_text[:5000])
            vector_store.upsert("resumes", [(str(resume.id), vec, {"filename": resume.filename, "candidate_id": str(resume.candidate_id)})])

    async def handle_match(payload):
        jid = uuid.UUID(payload['job_id'])
        cid = uuid.UUID(payload['candidate_id'])
        rid = uuid.UUID(payload['resume_id'])
        async with async_session() as session:
            jres = await session.execute(select(Job).where(Job.id == jid))
            job = jres.scalars().first()
            rres = await session.execute(select(Resume).where(Resume.id == rid))
            resume = rres.scalars().first()
            if not job or not resume:
                raise RuntimeError("Job or Resume not found")
            skill = calculate_skill_match(job.requirements, resume.skills or [])
            exp = calculate_experience_score(job.requirements, resume.experience_years)
            edu = calculate_education_score(resume.education_level)
            overall = calculate_overall_score(skill, exp, edu)
            sr = ScreeningResult(
                job_id=jid,
                candidate_id=cid,
                resume_id=rid,
                overall_score=overall,
                skill_match_score=skill,
                experience_score=exp,
                education_score=edu,
                detailed_analysis={
                    "skills": resume.skills or [],
                    "experience_years": resume.experience_years,
                    "education_level": resume.education_level,
                    "reasoning": f"Skill {skill*100:.0f}%, Exp {exp*100:.0f}%, Edu {edu*100:.0f}%",
                },
            )
            session.add(sr)
            await session.commit()

    task_queue.register_handler("parse_resume", handle_parse)
    task_queue.register_handler("match_candidate", handle_match)


_register_handlers()


