from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from typing import List
import logging
from app.services.rag_resume_parser import RAGResumeParser
from app.services.resumeparser import ResumeParser, FileParseError
from app.schemas.resumes import ParseResumeRequest, ParseResumeResponse
import os
from sqlalchemy import select, desc
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.core.security import decode_token
from app.core.config import settings
import uuid
from app.services.embeddings import get_embedding, vector_store

router = APIRouter(prefix="/resumes", tags=["resumes"])
logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = ["application/pdf", 
                      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
MAX_FILE_SIZE_MB = 10
UPLOAD_DIR = "./uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload and parse resume with skills standardization"""
    
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
        candidate = Candidate(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
            name="Candidate",
            email="candidate@example.com"
        )
        db.add(candidate)
        await db.commit()
        await db.refresh(candidate)

    # ===== VALIDATION =====
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}"
        )
    
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

    # ===== PARSE RESUME =====
    try:
        parser = ResumeParser()
        
        # Determine mimetype
        if filename.lower().endswith('.pdf'):
            mimetype = 'application/pdf'
        else:
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        
        # Parse resume (skills will be standardized in parser)
        parsed_data = parser.parse_resume(save_path, mimetype)
        
        logger.info(f"Resume parsed successfully. Skills: {parsed_data.get('skills', [])}")
        
    except FileParseError as e:
        os.remove(save_path)  # Clean up on error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        os.remove(save_path)  # Clean up on error
        logger.exception(f"Failed to parse resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse resume"
        )

    # ===== SAVE TO DATABASE =====
    resume = Resume(
        id=uuid.uuid4(),
        candidate_id=candidate.id,
        filename=filename,
        file_path=save_path,
        parsed_data=parsed_data,
        raw_text=parsed_data.get('raw_text'),
        skills=parsed_data.get('skills', []),  # ✅ NOW STANDARDIZED!
        experience_years=parsed_data.get('experience_years'),
        education_level=extract_education_level(parsed_data.get('education', []))
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    logger.info(f"Resume saved with ID: {resume.id}, Standardized Skills: {resume.skills}")

    # ===== UPSERT EMBEDDING =====
    try:
        text_for_embed = (parsed_data.get('raw_text') or '') + '\n' + ' '.join(parsed_data.get('skills', []))
        emb = get_embedding(text_for_embed[:5000])
        vector_store.upsert("resumes", [(str(resume.id), emb, {"filename": filename, "candidate_id": str(candidate.id)})])
    except Exception:
        logger.warning("Failed to upsert resume embedding; continuing")

    return {
        "message": "Resume uploaded successfully",
        "resume_id": str(resume.id),
        "filename": filename,
        "skills": resume.skills,  # ✅ Return standardized skills
        "parsed_data": parsed_data
    }


@router.post("/{resume_id}/parse", response_model=ParseResumeResponse)
async def parse_resume(
    resume_id: str, 
    parse_options: ParseResumeRequest,
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Parse resume with optional detailed extraction"""
    
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
        # Validate the token subject is a UUID string
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

    # Determine mimetype from filename
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
            logger.info("RAG parser used successfully")
        except Exception as e:
            logger.warning(f"RAG parser failed: {str(e)}")
            parsed = None

    # Use spaCy parser if RAG failed or not requested
    if not parsed or not parsed.get('skills'):
        try:
            parsed = spacy_parser.parse_resume(filepath, mimetype)
            logger.info(f"spaCy parser used. Skills: {parsed.get('skills', [])}")
        except FileParseError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": str(e),
                    "error_type": "parse_error",
                    "filename": resume_record.filename
                }
            )
    
    # ✅ STANDARDIZE SKILLS (Extra safety layer)
    if parsed and parsed.get('skills'):
        try:
            parsed['skills'] = spacy_parser.skills_standardizer.standardize_skills(
                parsed['skills']
            )
            logger.info(f"Skills standardized: {parsed['skills']}")
        except Exception as e:
            logger.warning(f"Skills standardization failed: {e}")
        
    # Enrich parse results if detailed extraction requested
    if parse_options.extract_detailed:
        try:
            detailed_exp = spacy_parser.extract_experience(parsed.get('raw_text', ''))
            detailed_edu = spacy_parser.extract_education(parsed.get('raw_text', ''))
            
            if detailed_exp:
                parsed['experience'] = detailed_exp
            if detailed_edu:
                parsed['education'] = detailed_edu
                
            logger.info(f"Detailed extraction completed. Experience: {len(detailed_exp)}, Education: {len(detailed_edu)}")
        except Exception as e:
            logger.warning(f"Detailed extraction failed: {str(e)}")

    # Persist parsed results to DB
    try:
        # Update resume record with parsed data
        resume_record.parsed_data = parsed
        resume_record.raw_text = parsed.get('raw_text')
        
        # Normalize and validate skills
        if isinstance(parsed.get('skills'), list):
            resume_record.skills = [s for s in parsed['skills'] if isinstance(s, str)]
        else:
            resume_record.skills = None
            
        # Save experience years
        experience_years = parsed.get('experience_years')
        if isinstance(experience_years, (int, float)):
            resume_record.experience_years = int(experience_years)
            
        # Extract education level
        education = parsed.get('education', [])
        resume_record.education_level = extract_education_level(education)
                
        # Save changes
        db.add(resume_record)
        await db.commit()
        await db.refresh(resume_record)
        
        logger.info(f"Resume {resume_id} parsed and saved. Skills: {resume_record.skills}")

        # Update embedding after re-parse
        try:
            text_for_embed = (parsed.get('raw_text') or '') + '\n' + ' '.join(parsed.get('skills', []))
            emb = get_embedding(text_for_embed[:5000])
            vector_store.upsert("resumes", [(str(resume_record.id), emb, {"filename": resume_record.filename, "candidate_id": str(resume_record.candidate_id)})])
        except Exception:
            logger.warning("Failed to upsert updated resume embedding")
        
    except Exception as e:
        await db.rollback()
        logger.exception(f"Failed to save parsed resume: {e}")
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

    return ParseResumeResponse(**parsed)


@router.get("/list")
async def list_resumes(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
    skill: list[str] | None = Query(None, description="Filter resumes that contain ANY of these skills"),
    min_experience_years: int | None = Query(None, ge=0, description="Minimum experience years"),
    education_contains: str | None = Query(None, description="Substring match on education level")
):
    """List all resumes for authenticated user with standardized skills"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    
    parts = authorization.split()
    user_id = decode_token(parts[1])
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get candidate
    candidate_result = await db.execute(
        select(Candidate).where(Candidate.user_id == user_id)
    )
    candidate = candidate_result.scalars().first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Get resumes
    query = select(Resume).where(Resume.candidate_id == candidate.id)
    # Filters
    from sqlalchemy import or_
    if skill:
        skill_filters = [Resume.skills.contains([s]) for s in skill if s]
        if skill_filters:
            query = query.where(or_(*skill_filters))
    if min_experience_years is not None:
        query = query.where(Resume.experience_years >= min_experience_years)
    if education_contains:
        query = query.where(Resume.education_level.ilike(f"%{education_contains}%"))

    query = query.order_by(desc(Resume.created_at))

    resumes = await db.execute(query)
    resumes = resumes.scalars().all()
    
    return {
        "resumes": [
            {
                "id": str(r.id),
                "filename": r.filename,
                "skills": r.skills or [],  # ✅ Already standardized
                "experience_years": r.experience_years,
                "education_level": r.education_level,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in resumes
        ]
    }


@router.get("/{resume_id}/details")
async def get_resume_details(
    resume_id: str,
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed resume information with standardized skills"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    
    parts = authorization.split()
    user_id = decode_token(parts[1])
    
    try:
        rid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid resume ID")
    
    # Get resume with ownership check
    result = await db.execute(
        select(Resume)
        .join(Candidate)
        .where(Resume.id == rid, Candidate.user_id == user_id)
    )
    resume = result.scalars().first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return {
        "id": str(resume.id),
        "filename": resume.filename,
        "parsed_data": resume.parsed_data,
        "raw_text": resume.raw_text,
        "skills": resume.skills or [],  # ✅ Standardized
        "experience_years": resume.experience_years,
        "education_level": resume.education_level,
        "created_at": resume.created_at.isoformat() if resume.created_at else None
    }


@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: str,
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Download a resume file"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    
    parts = authorization.split()
    user_id = decode_token(parts[1])
    
    try:
        rid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid resume ID")
    
    result = await db.execute(
        select(Resume)
        .join(Candidate)
        .where(Resume.id == rid, Candidate.user_id == user_id)
    )
    resume = result.scalars().first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    file_path = resume.file_path
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Return file download
    from fastapi.responses import FileResponse
    return FileResponse(
        path=file_path,
        filename=resume.filename,
        media_type='application/octet-stream'
    )


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db)
):
    """Delete a resume and its file"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    
    parts = authorization.split()
    user_id = decode_token(parts[1])
    
    try:
        rid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid resume ID")
    
    result = await db.execute(
        select(Resume)
        .join(Candidate)
        .where(Resume.id == rid, Candidate.user_id == user_id)
    )
    resume = result.scalars().first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Delete file
    if resume.file_path and os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
            logger.info(f"Deleted file: {resume.file_path}")
        except Exception as e:
            logger.warning(f"Failed to delete file: {e}")
    
    # Delete from DB
    await db.delete(resume)
    await db.commit()
    
    logger.info(f"Resume deleted: {resume_id}")
    
    return {"message": "Resume deleted successfully"}


# ========== HELPER FUNCTIONS ==========

def extract_education_level(education: List[dict]) -> str:
    """Extract education level from education entries"""
    if not education or not isinstance(education, list):
        return None
    
    try:
        if isinstance(education[0], dict):
            degree = education[0].get('degree', '')
        else:
            degree = str(education[0])
        
        return degree if degree else None
    except Exception:
        return None
