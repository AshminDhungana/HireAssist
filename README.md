# AI-Powered Resume Screening and Parsing System

## Overview

This system is a **comprehensive, production-ready Resume/CV Screening and Parsing System** built with modern technologies including **React**, **Tailwind CSS**, **Python FastAPI**, **RAG (Retrieval-Augmented Generation)**, and **LangChain**. The system leverages advanced AI techniques to automate resume screening, candidate ranking, and intelligent job matching.

## 🚀 Key Features

### Core Functionality
- **AI-Powered Resume Parsing**: Extract structured data from PDF/DOCX resumes using LangChain and NLP
- **Semantic Job Matching**: RAG-powered similarity search between resumes and job descriptions
- **Real-time Candidate Ranking**: Score and rank candidates using vector embeddings
- **Intelligent Screening**: Multi-criteria evaluation with customizable scoring algorithms
- **Interactive Dashboard**: Modern React interface with real-time updates

### Advanced AI Features
- **Vector Database Integration**: Pinecone/Qdrant for scalable semantic search
- **Hybrid Search**: Combines keyword-based and semantic matching
- **Entity Recognition**: Extract skills, experience, education using spaCy NER
- **Adaptive Retrieval**: RAG Fusion for complex job requirement queries
- **Conversation AI**: Chat interface for querying candidate database

### Enterprise Features
- **Role-Based Authentication**: JWT-based security with Admin/Recruiter/Candidate roles
- **Multi-tenant Architecture**: Support for multiple organizations
- **API-First Design**: RESTful APIs with comprehensive documentation
- **Scalable Infrastructure**: Docker containerization and cloud deployment ready
- **Analytics Dashboard**: Comprehensive recruitment metrics and insights

## 🛠 Tech Stack

### Frontend
- **React 18+** with TypeScript
- **Tailwind CSS** for responsive design
- **Redux Toolkit** for state management
- **React Query** for data fetching
- **Chart.js** for analytics visualization
- **React Hook Form** for form management

### Backend
- **FastAPI** with Python 3.11+
- **PostgreSQL** for primary database
- **Redis** for caching and sessions
- **Celery** for background tasks
- **SQLAlchemy** ORM with Alembic migrations
- **Pydantic** for data validation

### AI/ML Stack
- **LangChain** for RAG implementation
- **OpenAI GPT-4** for text analysis
- **Pinecone/Qdrant** vector database
- **spaCy** for NER and text processing
- **Sentence Transformers** for embeddings
- **FAISS** for local vector search

### Infrastructure
- **Docker** containerization
- **Docker Compose** for development
- **Nginx** reverse proxy
- **GitHub Actions** CI/CD
- **AWS/GCP** cloud deployment
- **Prometheus/Grafana** monitoring

## 📁 Project Structure

```
resume-screening-system/
├── frontend/                    # React application
│   ├── src/
│   │   ├── api/ 
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API service functions
│   │   ├── store/             # Redux store configuration
│   │   ├── types/             # TypeScript type definitions
│   │   └── utils/             # Utility functions
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts
├── backend/                     # FastAPI application
│   ├── app/
│   │   ├── api/               # API route handlers
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── resumes.py
│   │   │   │   ├── jobs.py
│   │   │   │   └── analytics.py
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   │   ├── resume_parser.py
│   │   │   ├── rag_engine.py
│   │   │   ├── matching_service.py
│   │   │   └── ai_service.py
│   │   ├── utils/             # Utility functions
│   │   └── dependencies.py    # FastAPI dependencies
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Test suite
│   ├── requirements.txt
│   └── Dockerfile
├── ai-services/                # AI/ML microservices
│   ├── resume-parser/         # Resume parsing service
│   ├── rag-engine/           # RAG implementation
│   └── vector-db/            # Vector database service
├── infrastructure/            # Infrastructure as Code
│   ├── docker/
│   ├── kubernetes/
│   └── terraform/
├── docs/                      # Documentation
├── scripts/                   # Deployment scripts
├── docker-compose.yml
├── docker-compose.prod.yml
└── README.md
```

## 🗄 Database Schema

### Core Tables
```sql
-- Users and Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL, -- admin, recruiter, candidate
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Organizations (Multi-tenant)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(100),
    settings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Job Postings
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT,
    location VARCHAR(255),
    salary_range INT4RANGE,
    status VARCHAR(50) DEFAULT 'active',
    embedding VECTOR(1536), -- OpenAI embedding
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Candidates and Resumes
CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    location VARCHAR(255),
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID REFERENCES candidates(id),
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    parsed_data JSONB, -- Structured resume data
    raw_text TEXT,
    embedding VECTOR(1536),
    skills TEXT[],
    experience_years INTEGER,
    education_level VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Job Applications and Screening Results
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    candidate_id UUID REFERENCES candidates(id),
    resume_id UUID REFERENCES resumes(id),
    status VARCHAR(50) DEFAULT 'submitted',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE screening_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID REFERENCES applications(id),
    overall_score DECIMAL(5,2),
    skill_match_score DECIMAL(5,2),
    experience_score DECIMAL(5,2),
    education_score DECIMAL(5,2),
    detailed_analysis JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🤖 AI Architecture

### RAG Pipeline Architecture
```
1. Document Ingestion
   ├── Resume Upload (PDF/DOCX)
   ├── Text Extraction (PyPDF2, python-docx)
   └── Text Preprocessing

2. Information Extraction
   ├── Named Entity Recognition (spaCy)
   ├── Skill Extraction (Custom NER Model)
   └── Structured Data Generation

3. Vector Embedding
   ├── Text Chunking (LangChain)
   ├── Embedding Generation (OpenAI/Sentence-BERT)
   └── Vector Storage (Pinecone/Qdrant)

4. Retrieval & Ranking
   ├── Semantic Search
   ├── Hybrid Search (Dense + Sparse)
   ├── Re-ranking Algorithm
   └── Score Calculation

5. Generation & Response
   ├── Context Augmentation
   ├── LLM-based Analysis
   └── Structured Output
```

### Matching Algorithm
```python
class CandidateMatchingService:
    def calculate_match_score(self, resume_data, job_requirements):
        """
        Multi-dimensional matching algorithm
        """
        scores = {
            'skill_match': self._calculate_skill_similarity(resume_data, job_requirements),
            'experience_match': self._calculate_experience_score(resume_data, job_requirements),
            'education_match': self._calculate_education_score(resume_data, job_requirements),
            'semantic_similarity': self._calculate_semantic_similarity(resume_data, job_requirements)
        }
        
        # Weighted scoring
        weights = {'skill_match': 0.4, 'experience_match': 0.3, 
                  'education_match': 0.2, 'semantic_similarity': 0.1}
        
        overall_score = sum(scores[key] * weights[key] for key in scores)
        return overall_score, scores
```

## 🔐 Authentication & Security

### JWT Implementation
```python
# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Role-based access control
class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: User = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user

# Usage in routes
@router.post("/jobs", dependencies=[Depends(RoleChecker(["admin", "recruiter"]))])
async def create_job(job_data: JobCreate, current_user: User):
    # Job creation logic
    pass
```

## 🚀 Deployment Guide

### Development Setup
```bash
# Clone repository
git clone https://github.com/yourusername/resume-screening-system.git
cd resume-screening-system

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database setup
alembic upgrade head

# Environment variables
cp .env.example .env
# Edit .env with your configuration

# Start backend
uvicorn app.main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev

# Start with Docker Compose
docker-compose up -d
```

### Production Deployment
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# With Kubernetes
kubectl apply -f infrastructure/kubernetes/
```

### Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/resume_screening
REDIS_URL=redis://localhost:6379

# AI Services
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=us-west1-gcp

# Authentication
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Storage
UPLOAD_FOLDER=./uploads
MAX_FILE_SIZE=10485760  # 10MB

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## 📊 API Documentation

### Authentication Endpoints
```
POST /api/v1/auth/login      # User login
POST /api/v1/auth/register   # User registration
POST /api/v1/auth/refresh    # Refresh token
POST /api/v1/auth/logout     # Logout user
```

### Resume Management
```
POST /api/v1/resumes/upload     # Upload resume
GET  /api/v1/resumes/{id}       # Get resume details
PUT  /api/v1/resumes/{id}       # Update resume
DELETE /api/v1/resumes/{id}     # Delete resume
GET  /api/v1/resumes/parse/{id} # Parse resume content
```

### Job Management
```
POST /api/v1/jobs           # Create job posting
GET  /api/v1/jobs           # List jobs
GET  /api/v1/jobs/{id}      # Get job details
PUT  /api/v1/jobs/{id}      # Update job
DELETE /api/v1/jobs/{id}    # Delete job
```

### Screening & Matching
```
POST /api/v1/screening/match     # Match resumes to job
GET  /api/v1/screening/results   # Get screening results
POST /api/v1/screening/bulk      # Bulk screening
GET  /api/v1/screening/analytics # Screening analytics
```

## 🧪 Testing Strategy

### Backend Testing
```python
# Test structure
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── fixtures/         # Test data fixtures
└── conftest.py       # Pytest configuration

# Example test
@pytest.mark.asyncio
async def test_resume_parsing():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/resumes/upload",
            files={"file": ("test_resume.pdf", file_content, "application/pdf")}
        )
        assert response.status_code == 201
        assert "parsed_data" in response.json()
```

### Frontend Testing
```typescript
// Component testing with React Testing Library
import { render, screen } from '@testing-library/react';
import { ResumeUpload } from './ResumeUpload';

test('renders resume upload component', () => {
  render(<ResumeUpload />);
  expect(screen.getByText(/upload resume/i)).toBeInTheDocument();
});
```

## 🔧 Performance Optimization

### Caching Strategy
```python
# Redis caching
@cache(expire=3600)  # 1 hour cache
async def get_job_matches(job_id: str, limit: int = 50):
    # Expensive matching operation
    return await matching_service.find_candidates(job_id, limit)
```

### Database Optimization
```sql
-- Indexes for performance
CREATE INDEX idx_resumes_skills ON resumes USING GIN(skills);
CREATE INDEX idx_resumes_embedding ON resumes USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
```

## 📈 Monitoring & Analytics

### Metrics Collection
```python
# Prometheus metrics
from prometheus_client import Counter, Histogram

resume_uploads = Counter('resume_uploads_total', 'Total resume uploads')
screening_duration = Histogram('screening_duration_seconds', 'Time spent screening')

@router.post("/resumes/upload")
async def upload_resume():
    resume_uploads.inc()
    with screening_duration.time():
        # Processing logic
        pass
```

### Health Checks
```python
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": await check_database_connection(),
        "redis": await check_redis_connection(),
        "vector_db": await check_vector_db_connection()
    }
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models and embeddings
- LangChain for RAG framework
- FastAPI for the excellent web framework
- React team for the frontend framework
- spaCy for NLP capabilities

---

**Built with ❤️ for modern recruitment workflows**