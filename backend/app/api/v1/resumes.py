from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from typing import List
import logging
from app.services.rag_resume_parser import RAGResumeParser
from app.services.resumeparser import ResumeParser, FileParseError
from app.schemas.resumes import ParseResumeRequest, ParseResumeResponse
import os
from sqlalchemy import select
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.core.security import decode_token
from app.core.config import settings
import uuid

router = APIRouter(prefix="/resumes")

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



@router.post("/{resume_id}/parse", response_model=ParseResumeResponse)
async def parse_resume(
    resume_id: str, 
    parse_options: ParseResumeRequest,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    # Validate auth token
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    
    try:
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise ValueError("Invalid token format")
        token = parts[1]
        user_id = decode_token(token)
        if not user_id:
            raise ValueError("Invalid token")
        # Validate the token subject is a UUID string; otherwise reject early to avoid DB errors
        try:
            user_uuid = uuid.UUID(user_id)
        except Exception:
            raise ValueError("Invalid token subject")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

    # Load and validate resume record
    try:
        uid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid resume id format"
        )

    result = await db.execute(
        select(Resume)
        .join(Candidate)
        .where(Resume.id == uid, Candidate.user_id == user_uuid)
    )
    resume_record = result.scalars().first()

    if not resume_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Resume not found or access denied"
        )

    filepath = resume_record.file_path
    if not filepath or not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Resume file not found on disk"
        )

    # Determine mimetype from filename with additional validation
    filename = (resume_record.filename or "").lower()
    if filename.endswith('.pdf'):
        mimetype = 'application/pdf'
    elif filename.endswith('.docx'):
        mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {filename.split('.')[-1]}"
        )

    # Initialize parsers based on request options
    spacy_parser = ResumeParser()
    parsed = None
    
    # Try RAG if requested and configured
    if parse_options.use_rag and getattr(settings, 'USE_RAG_PARSER', False):
        try:
            rag_parser = RAGResumeParser()
            parsed = rag_parser.parse_resume(filepath, mimetype)
        except Exception as e:
            logger.warning("RAG parser failed: %s", str(e))
            parsed = None

    # Use spaCy parser if RAG failed or not requested
    if not parsed or not parsed.get('skills'):
        try:
            parsed = spacy_parser.parse_resume(filepath, mimetype)
        except FileParseError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": str(e),
                    "error_type": "parse_error",
                    "filename": resume_record.filename
                }
            )
        
    # Enrich parse results if detailed extraction requested
    if parse_options.extract_detailed:
        try:
            # Attempt more detailed parsing of experience and education
            detailed_exp = spacy_parser.extract_experience(parsed.get('raw_text', ''))
            detailed_edu = spacy_parser.extract_education(parsed.get('raw_text', ''))
            
            if detailed_exp:
                parsed['experience'] = detailed_exp
            if detailed_edu:
                parsed['education'] = detailed_edu
        except Exception as e:
            logger.warning("Detailed extraction failed: %s", str(e))

    # Persist parsed results to DB with improved error handling
    try:
        # Update resume record with parsed data
        resume_record.parsed_data = parsed
        resume_record.raw_text = parsed.get('raw_text')
        
        # Normalize and validate fields before saving
        if isinstance(parsed.get('skills'), list):
            resume_record.skills = [s for s in parsed['skills'] if isinstance(s, str)]
        else:
            resume_record.skills = None
            
        experience_years = parsed.get('experience_years')
        if isinstance(experience_years, (int, float)):
            resume_record.experience_years = int(experience_years)
            
        # Extract education level from structured data
        education = parsed.get('education', [])
        if isinstance(education, list) and education:
            if isinstance(education[0], dict):
                resume_record.education_level = education[0].get('degree')
            else:
                resume_record.education_level = str(education[0])
                
        # Save changes
        db.add(resume_record)
        await db.commit()
        await db.refresh(resume_record)
        
    except Exception as e:
        await db.rollback()
        logger.exception("Failed to save parsed resume: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to save parsed results",
                "error_type": "database_error",
                "resume_id": str(resume_id)
            }
        )

    # Add confidence score if missing
    if 'confidence_score' not in parsed:
        required_fields = [
            bool(parsed.get('raw_text')),
            bool(parsed.get('skills')),
            bool(parsed.get('experience')),
            bool(parsed.get('education')),
            bool(parsed.get('personal_info', {}).get('name')),
            bool(parsed.get('personal_info', {}).get('email'))
        ]
        parsed['confidence_score'] = round(sum(1 for f in required_fields if f) / len(required_fields), 2)

    # Return parsed data through Pydantic validation
    return ParseResumeResponse(**parsed)

