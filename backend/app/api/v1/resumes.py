from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from typing import List
from app.services.rag_resume_parser import RAGResumeParser
from app.services.resumeparser import ResumeParser
import os
from fastapi import Header
from sqlalchemy import ForeignKey
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
from sqlalchemy import select
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.core.security import decode_token
import uuid

router = APIRouter()

ALLOWED_MIME_TYPES = ["application/pdf", 
                      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
MAX_FILE_SIZE_MB = 10
UPLOAD_DIR = "./uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    # ===== AUTHENTICATION =====
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    
    # Extract token
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
    
    # Decode token to get user_id
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Get candidate for this user
    candidate = await db.execute(
        select(Candidate).where(Candidate.user_id == user_id)
    )
    candidate = candidate.scalars().first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found. Please create candidate profile first."
        )
    
 
    # ===== VALIDATION =====
    # Allow None content_type for PDFs (sometimes not detected)
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}"
        )
    
    # Check file extension instead
    if not file.filename.lower().endswith(('.pdf', '.docx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are allowed"
        )


    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Max size: 10MB"
        )

    # ===== SAVE FILE =====
    filename = file.filename.replace("/", "_").replace("\\", "_")
    save_path = os.path.join(UPLOAD_DIR, filename)

    with open(save_path, "wb") as f:
        f.write(contents)

    # ===== SAVE TO DATABASE =====
    resume = Resume(
        id=uuid.uuid4(),
        candidate_id=candidate.id,
        filename=filename,
        file_path=save_path,
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    return {
        "message": "Resume uploaded successfully",
        "resume_id": str(resume.id),
        "filename": filename
    }



@router.post("/{resume_id}/parse")
async def parse_resume(resume_id: str, db: AsyncSession = Depends(get_db)):
    # Load file info
    resume_record = await db.get_resume_record(resume_id)
    filepath = resume_record.file_path
    mimetype = resume_record.file_mime_type

    # 1. Parse with RAG (LLM)
    rag_parser = RAGResumeParser()
    rag_result = rag_parser.parse_resume(filepath, mimetype)

    # 2. Fallback/Ensemble: If LLM was incomplete, run spaCy parser (or always run for comparison)
    if not rag_result.get("skills") or "raw_output" in rag_result:
        spacy_parser = ResumeParser()
        spacy_result = spacy_parser.parse_resume(filepath, mimetype)
        for key in ["skills", "experience", "education", "personal_info"]:
            if not rag_result.get(key):
                rag_result[key] = spacy_result.get(key)


    await db.save_parsed_resume(resume_id, rag_result)
    return rag_result

