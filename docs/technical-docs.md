# Project Documentation Suite

## 1. System Architecture Document

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   AI Services   │
│   React + TS    │────│   FastAPI       │────│   LangChain     │
│   Tailwind CSS  │    │   Authentication│    │   RAG Engine    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
         v                        v                        v
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CDN/Storage   │    │   Database      │    │  Vector Store   │
│   File uploads  │    │   PostgreSQL    │    │  Pinecone/      │
│   Resume files  │    │   User/Job data │    │  Qdrant         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Breakdown
- **Frontend Layer**: React SPA with Tailwind CSS for responsive UI
- **API Layer**: FastAPI with async support and OpenAPI documentation
- **AI Processing**: LangChain-based RAG system with vector embeddings
- **Data Layer**: PostgreSQL for relational data, Redis for caching
- **Vector Storage**: Pinecone/Qdrant for semantic search capabilities
- **File Storage**: AWS S3 or local storage for resume files

## 2. Business Requirements Document (BRD)

### Project Objectives
1. **Automate Resume Screening**: Reduce manual effort in initial candidate screening
2. **Improve Matching Accuracy**: Use AI to match candidates to job requirements
3. **Enhance Recruiter Productivity**: Provide intelligent insights and recommendations
4. **Scale Recruitment Process**: Handle large volumes of applications efficiently

### Functional Requirements
- **FR1**: System shall parse resumes in PDF and DOCX formats
- **FR2**: System shall extract structured data (skills, experience, education)
- **FR3**: System shall match resumes to job descriptions using semantic similarity
- **FR4**: System shall rank candidates based on job fit score
- **FR5**: System shall provide conversational interface for candidate queries
- **FR6**: System shall support role-based access (Admin, Recruiter, Candidate)

### Success Metrics
- **Time Reduction**: 70% reduction in initial screening time
- **Accuracy**: >85% accuracy in skill extraction and matching
- **User Adoption**: 90% of recruiters actively using the system
- **Processing Speed**: <5 seconds per resume parsing

## 3. Technical Specification Document

### API Design Specification

#### Authentication Endpoints
```python
# POST /api/v1/auth/login
{
    "username": "string",
    "password": "string"
}

# Response
{
    "access_token": "string",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
        "id": "uuid",
        "email": "string",
        "role": "string"
    }
}
```

#### Resume Processing Endpoints
```python
# POST /api/v1/resumes/upload
Content-Type: multipart/form-data
{
    "file": "binary",
    "job_id": "uuid" (optional)
}

# Response
{
    "resume_id": "uuid",
    "filename": "string",
    "status": "processing|completed|failed",
    "parsed_data": {
        "personal_info": {...},
        "skills": [...],
        "experience": [...],
        "education": [...]
    }
}
```

#### Job Matching Endpoints
```python
# POST /api/v1/jobs/{job_id}/match
{
    "filters": {
        "min_experience": 2,
        "required_skills": ["Python", "FastAPI"],
        "location": "Remote"
    },
    "limit": 50
}

# Response
{
    "matches": [
        {
            "candidate_id": "uuid",
            "resume_id": "uuid",
            "match_score": 0.87,
            "skill_match": 0.9,
            "experience_match": 0.8,
            "details": {...}
        }
    ]
}
```

### Database Schema Design
```sql
-- Extended schema with performance optimization
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Users table with role-based access
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role user_role NOT NULL DEFAULT 'candidate',
    organization_id UUID REFERENCES organizations(id),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Organizations for multi-tenancy
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(100),
    logo_url VARCHAR(500),
    settings JSONB DEFAULT '{}',
    subscription_plan VARCHAR(50) DEFAULT 'basic',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Job postings with vector embeddings
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id),
    created_by UUID REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT,
    location VARCHAR(255),
    employment_type job_type DEFAULT 'full_time',
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency VARCHAR(3) DEFAULT 'USD',
    remote_allowed BOOLEAN DEFAULT false,
    experience_min INTEGER DEFAULT 0,
    experience_max INTEGER,
    required_skills TEXT[],
    preferred_skills TEXT[],
    status job_status DEFAULT 'active',
    description_embedding VECTOR(1536),
    requirements_embedding VECTOR(1536),
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Candidates and their profiles
CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    location VARCHAR(255),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    summary TEXT,
    current_title VARCHAR(255),
    experience_years INTEGER DEFAULT 0,
    expected_salary INTEGER,
    currency VARCHAR(3) DEFAULT 'USD',
    availability DATE,
    profile_embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resume storage and parsing results
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID REFERENCES candidates(id),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(100),
    raw_text TEXT,
    parsed_data JSONB,
    parsing_status parsing_status DEFAULT 'pending',
    parsing_error TEXT,
    text_embedding VECTOR(1536),
    skills_extracted TEXT[],
    entities_extracted JSONB,
    language VARCHAR(5) DEFAULT 'en',
    confidence_score DECIMAL(3,2),
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Applications and their lifecycle
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id),
    candidate_id UUID REFERENCES candidates(id),
    resume_id UUID REFERENCES resumes(id),
    status application_status DEFAULT 'submitted',
    cover_letter TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Screening results
    overall_score DECIMAL(5,2),
    skill_match_score DECIMAL(5,2),
    experience_score DECIMAL(5,2),
    education_score DECIMAL(5,2),
    location_score DECIMAL(5,2),
    salary_compatibility DECIMAL(5,2),
    
    -- Detailed analysis
    detailed_analysis JSONB,
    missing_skills TEXT[],
    matching_keywords TEXT[],
    screening_notes TEXT,
    screened_by UUID REFERENCES users(id),
    screened_at TIMESTAMP
);

-- Performance indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_organization ON users(organization_id);
CREATE INDEX idx_jobs_organization ON jobs(organization_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created ON jobs(created_at);
CREATE INDEX idx_candidates_user ON candidates(user_id);
CREATE INDEX idx_resumes_candidate ON resumes(candidate_id);
CREATE INDEX idx_resumes_status ON resumes(parsing_status);
CREATE INDEX idx_applications_job ON applications(job_id);
CREATE INDEX idx_applications_candidate ON applications(candidate_id);
CREATE INDEX idx_applications_status ON applications(status);

-- Vector similarity indexes (for pgvector)
CREATE INDEX idx_jobs_desc_embedding ON jobs USING ivfflat (description_embedding vector_cosine_ops);
CREATE INDEX idx_resumes_embedding ON resumes USING ivfflat (text_embedding vector_cosine_ops);

-- GIN indexes for JSONB and array columns
CREATE INDEX idx_resumes_skills ON resumes USING GIN(skills_extracted);
CREATE INDEX idx_jobs_skills ON jobs USING GIN(required_skills);
CREATE INDEX idx_resumes_parsed_data ON resumes USING GIN(parsed_data);
```

## 4. AI/ML Implementation Guide

### RAG System Architecture
```python
class RAGResumeScreeningSystem:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = PineconeVectorStore()
        self.llm = ChatOpenAI(model="gpt-4")
        self.retriever = self.vector_store.as_retriever()
        
    def process_resume(self, file_path: str) -> dict:
        """Complete resume processing pipeline"""
        # 1. Extract text
        text = self.extract_text(file_path)
        
        # 2. Parse with NER
        entities = self.extract_entities(text)
        
        # 3. Generate embeddings
        embedding = self.embeddings.embed_query(text)
        
        # 4. Store in vector database
        doc_id = self.vector_store.add_texts([text], [embedding])
        
        return {
            "text": text,
            "entities": entities,
            "embedding_id": doc_id,
            "structured_data": self.structure_data(entities)
        }
    
    def match_candidates(self, job_description: str, top_k: int = 20):
        """Find best matching candidates"""
        # 1. Generate job embedding
        job_embedding = self.embeddings.embed_query(job_description)
        
        # 2. Similarity search
        similar_docs = self.vector_store.similarity_search_by_vector(
            job_embedding, k=top_k
        )
        
        # 3. Re-rank with LLM
        candidates = []
        for doc in similar_docs:
            analysis = self.analyze_match(job_description, doc.page_content)
            candidates.append({
                "document_id": doc.metadata["id"],
                "similarity_score": doc.metadata["score"],
                "llm_analysis": analysis
            })
            
        return sorted(candidates, key=lambda x: x["llm_analysis"]["score"], reverse=True)
```

### NER Model Implementation
```python
import spacy
from spacy.training import Example

class ResumeNERTrainer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_trf")
        self.custom_labels = [
            "SKILL", "DEGREE", "CERTIFICATION", 
            "COMPANY", "POSITION", "DURATION"
        ]
    
    def train_custom_ner(self, training_data):
        """Train custom NER model for resume parsing"""
        ner = self.nlp.get_pipe("ner")
        
        # Add custom labels
        for label in self.custom_labels:
            ner.add_label(label)
        
        # Training loop
        optimizer = self.nlp.begin_training()
        for epoch in range(50):
            losses = {}
            for text, annotations in training_data:
                example = Example.from_dict(self.nlp.make_doc(text), annotations)
                self.nlp.update([example], losses=losses, sgd=optimizer)
        
        self.nlp.to_disk("./models/resume_ner_model")
```

## 5. Testing Documentation

### Test Strategy
```python
# pytest configuration
# conftest.py
@pytest.fixture
async def test_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def test_db():
    # Create test database
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Integration tests
@pytest.mark.asyncio
async def test_resume_processing_pipeline(test_client, test_db):
    # Test complete resume processing flow
    with open("test_resume.pdf", "rb") as file:
        response = await test_client.post(
            "/api/v1/resumes/upload",
            files={"file": ("resume.pdf", file, "application/pdf")}
        )
    
    assert response.status_code == 201
    resume_data = response.json()
    
    # Verify parsing results
    assert "parsed_data" in resume_data
    assert "skills_extracted" in resume_data
    assert len(resume_data["skills_extracted"]) > 0

# Performance tests
@pytest.mark.performance
async def test_bulk_resume_processing():
    start_time = time.time()
    
    # Process 100 resumes
    tasks = []
    for i in range(100):
        task = process_resume(f"test_resume_{i}.pdf")
        tasks.append(task)
    
    await asyncio.gather(*tasks)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Should process 100 resumes in under 30 seconds
    assert processing_time < 30
```

## 6. Deployment Guide

### Docker Configuration
```dockerfile
# Multi-stage Dockerfile for production
FROM python:3.11-slim as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

FROM python-base as builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python-base as runtime
COPY --from=builder /root/.local /root/.local
WORKDIR /app
COPY . .

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Kubernetes Deployment
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: resume-screening-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: resume-screening-api
  template:
    metadata:
      labels:
        app: resume-screening-api
    spec:
      containers:
      - name: api
        image: resume-screening:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

## 7. Security Implementation

### Authentication & Authorization
```python
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

class SecurityService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.ALGORITHM = "HS256"
    
    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

# Role-based access control
class RolePermissions:
    PERMISSIONS = {
        "admin": ["*"],
        "recruiter": [
            "jobs:create", "jobs:read", "jobs:update", "jobs:delete",
            "resumes:read", "applications:read", "screening:execute"
        ],
        "candidate": [
            "resumes:create", "resumes:read", "resumes:update",
            "applications:create", "applications:read"
        ]
    }
    
    @classmethod
    def check_permission(cls, user_role: str, required_permission: str) -> bool:
        role_permissions = cls.PERMISSIONS.get(user_role, [])
        return "*" in role_permissions or required_permission in role_permissions
```

## 8. Monitoring and Analytics

### Application Metrics
```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics collection
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_USERS = Gauge('active_users', 'Number of active users')
RESUME_PROCESSING_TIME = Histogram('resume_processing_seconds', 'Resume processing time')

class MetricsMiddleware:
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        # Record metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path
        ).inc()
        
        REQUEST_DURATION.observe(time.time() - start_time)
        
        return response
```

This comprehensive documentation suite provides all the necessary technical specifications, implementation guides, and operational procedures needed to build and deploy a production-ready Resume/CV Screening and Parsing System.