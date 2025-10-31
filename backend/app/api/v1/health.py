from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint for API status monitoring"""
    return {
        "status": "healthy",
        "message": "API is running"
    }
