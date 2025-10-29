from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
from app.services.rag_resume_parser import RAGResumeParser
from app.services.resumeparser import ResumeParser
import os
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

router = APIRouter()

ALLOWED_MIME_TYPES = ["application/pdf", 
                      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
MAX_FILE_SIZE_MB = 10
UPLOAD_DIR = "./uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(file: UploadFile = File(...)):
    # Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}"
        )

    # Read file bytes and check size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Max size: 10MB"
        )

    # Clean filename (prevent traversal)
    filename = file.filename.replace("/", "_").replace("\\", "_")
    save_path = os.path.join(UPLOAD_DIR, filename)

    # Save file securely
    with open(save_path, "wb") as f:
        f.write(contents)

    return {"message": "Resume uploaded successfully.", "filename": filename}


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

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    parsed_data = Column(JSON)  # stores output from parsing pipeline
    created_at = Column(DateTime, server_default=func.now())
    # Uncomment and configure for vector DB embedding integration:
    # embedding = Column(Vector(1536))  # pgvector support