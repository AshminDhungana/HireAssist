from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, resumes
from app.core.database import engine, Base

app = FastAPI(
    title="HireAssist API",
    description="AI-Powered Resume Screening and Parsing System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

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
