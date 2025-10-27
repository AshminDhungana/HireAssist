from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
import os

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
