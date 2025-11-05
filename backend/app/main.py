from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from contextlib import asynccontextmanager
from datetime import datetime
import logging
import uuid

# API routers
from app.api.v1 import auth, resumes, candidates, jobs, matching, health, analytics, vectors, tasks, admin
from app.api.v1.skills import router as skills_router

# Core modules
from app.core.database import engine, Base, async_session
from app.core.middleware import (
    global_error_handler, 
    request_context_middleware, 
    rate_limit_middleware, 
    security_headers_middleware
)
from app.core.metrics import record_request, export_prometheus
from app.core.security import get_password_hash

# Models & Exceptions
from app.models.users import User
from app.services.resumeparser import FileParseError
from sqlalchemy import select

logger = logging.getLogger(__name__)


# ========== STARTUP & SHUTDOWN ==========

async def create_superuser_admin():
    """Create superuser admin on startup if it doesn't exist"""
    try:
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.email == 'admin@hireassist.com')
            )
            existing_admin = result.scalars().first()
            
            if existing_admin:
                logger.info("✅ Superuser admin already exists")
                return
            
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
    logger.info("🚀 Starting HireAssist API...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables created/verified")
    
    await create_superuser_admin()
    
    try:
        from app.services.task_queue import task_queue
        await task_queue.start()
        logger.info("✅ Task queue worker started")
    except Exception as e:
        logger.warning(f"⚠️ Task queue not started: {e}")

    logger.info("✅ HireAssist API started successfully!")
    
    yield
    
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

# Add CORS middleware FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handling middleware
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next):
    return await global_error_handler(request, call_next)

# Request context middleware
@app.middleware("http")
async def add_request_context(request: Request, call_next):
    return await request_context_middleware(request, call_next)

# Rate limiting middleware
@app.middleware("http")
async def apply_rate_limit(request: Request, call_next):
    return await rate_limit_middleware(request, call_next)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    return await security_headers_middleware(request, call_next)

# Metrics middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = datetime.utcnow()
    response = await call_next(request)
    duration_ms = int((datetime.utcnow() - start).total_seconds() * 1000)
    try:
        record_request(request.url.path, response.status_code, duration_ms)
    except Exception as e:
        logger.warning(f"Metrics recording failed: {e}")
    return response


# ========== ROOT ENDPOINT ==========

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "HireAssist Backend is running!",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/v1/health"
    }


# ========== API ROUTERS ==========

# ✅ INCLUDE HEALTH ROUTER FIRST (creates /api/v1/health)
app.include_router(health.router, prefix="/api/v1", tags=["health"])

# Include other routers
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
app.include_router(resumes.router, prefix="/api/v1", tags=["resumes"])
app.include_router(candidates.router, prefix="/api/v1", tags=["candidates"])
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])
app.include_router(matching.router, prefix="/api/v1", tags=["matching"])
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
app.include_router(skills_router, prefix="/api/v1/skills", tags=["skills"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(vectors.router, prefix="/api/v1", tags=["vectors"])
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])


# ========== METRICS ENDPOINT ==========

@app.get("/api/v1/metrics")
def prometheus_metrics():
    """Export Prometheus metrics"""
    return Response(
        content=export_prometheus(),
        media_type="text/plain; version=0.0.4"
    )


# ========== EXCEPTION HANDLERS ==========

@app.exception_handler(FileParseError)
async def file_parse_error_handler(request: Request, exc: FileParseError):
    """Handle resume parsing errors"""
    logger.exception("FileParseError: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


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
