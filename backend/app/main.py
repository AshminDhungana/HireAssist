from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1 import auth, resumes, candidates, jobs, matching, health
from app.core.database import engine, Base, async_session
from fastapi.responses import JSONResponse
from app.services.resumeparser import FileParseError
from app.core.middleware import global_error_handler
from app.models.users import User
from app.core.security import get_password_hash
from sqlalchemy import select
from app.api.v1.skills import router as skills_router
import logging
import asyncio
import uuid
from app.api.v1 import admin
from datetime import datetime


logger = logging.getLogger(__name__)

# ========== STARTUP & SHUTDOWN ==========

async def create_superuser_admin():
    """Create superuser admin on startup if it doesn't exist"""
    try:
        async with async_session() as session:
            # Check if admin already exists
            result = await session.execute(
                select(User).where(User.email == 'admin@hireassist.com')
            )
            existing_admin = result.scalars().first()
            
            if existing_admin:
                logger.info("✅ Superuser admin already exists")
                return
            
            # Create superuser admin
            admin_user = User(
                id=uuid.uuid4(),
                email='admin@hireassist.com',
                password_hash=get_password_hash('AdminPassword123!'),
                first_name='Admin',
                last_name='User',
                role='admin',
                is_approved=True,
                created_at=datetime.utcnow()
            )
            
            session.add(admin_user)
            await session.commit()
            
            logger.info("=" * 60)
            logger.info("✅ SUPERUSER ADMIN CREATED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info("📋 Admin Credentials:")
            logger.info("   Email: admin@hireassist.com")
            logger.info("   Password: AdminPassword123!")
            logger.info("=" * 60)
            logger.info("⚠️  IMPORTANT: Change password after first login!")
            logger.info("=" * 60)
            
    except Exception as e:
        logger.error(f"❌ Error creating superuser admin: {str(e)}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # STARTUP
    logger.info("🚀 Starting HireAssist API...")
    
    # Create all database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables created/verified")
    
    # Create superuser admin
    await create_superuser_admin()
    
    logger.info("✅ HireAssist API started successfully!")
    
    yield
    
    # SHUTDOWN
    logger.info("🛑 Shutting down HireAssist API...")


# ========== FASTAPI APP ==========

app = FastAPI(
    title="HireAssist API",
    description="AI-Powered Resume Screening and Parsing System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)


# ========== MIDDLEWARE ==========

# Add global error handling middleware first
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    return await global_error_handler(request, call_next)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:3001"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== HEALTH CHECK ENDPOINTS ==========

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "HireAssist Backend is running!",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint for API status monitoring"""
    return {
        "status": "healthy",
        "message": "API is running",
        "timestamp": datetime.utcnow().isoformat()
    }


# ========== API ROUTERS ==========

app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
app.include_router(resumes.router, prefix="/api/v1", tags=["resumes"])
app.include_router(candidates.router, prefix="/api/v1/candidates", tags=["candidates"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(matching.router, prefix="/api/v1/matching", tags=["matching"])
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
app.include_router(skills_router, prefix="/api/v1/skills", tags=["skills"])



# ========== EXCEPTION HANDLERS ==========

# Central exception handler for parse errors
@app.exception_handler(FileParseError)
async def file_parse_error_handler(request, exc: FileParseError):
    logger.exception("FileParseError: %s", exc)
    return JSONResponse(status_code=400, content={"detail": str(exc)})


# ========== TEST ENDPOINTS ==========

@app.get("/api/v1/test-error")
def test_error():
    """Test endpoint for error handling verification"""
    raise Exception("Test induced error")


# ========== LOGGING CONFIG ==========

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
