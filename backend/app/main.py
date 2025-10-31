from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, resumes, candidates
from app.core.database import engine, Base
from fastapi.responses import JSONResponse
from app.services.resumeparser import FileParseError
from app.core.middleware import global_error_handler
import logging

app = FastAPI(
    title="HireAssist API",
    description="AI-Powered Resume Screening and Parsing System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add global error handling middleware first
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    return await global_error_handler(request, call_next)

#must be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
def root():
    return {"message": "HireAssist Backend is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Include API routers
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
app.include_router(resumes.router, prefix="/api/v1", tags=["resumes"])
app.include_router(candidates.router, prefix="/api/v1", tags=["candidates"])


# Small test-only endpoint used by unit tests to verify global error handling
@app.get("/api/v1/test-error")
def _test_error():
    raise Exception("Test induced error")


# Central exception handler for parse errors
@app.exception_handler(FileParseError)
async def file_parse_error_handler(request, exc: FileParseError):
    logging.getLogger(__name__).exception("FileParseError: %s", exc)
    return JSONResponse(status_code=400, content={"detail": str(exc)})

