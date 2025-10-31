# HireAssist - AI-Powered Resume Screening and Parsing System

## Overview

This system is a **comprehensive, production-ready Resume/CV Screening and Parsing System** built with modern technologies including **React**, **Tailwind CSS**, **Python FastAPI**, **RAG (Retrieval-Augmented Generation)**, and **LangChain**. The system leverages advanced AI techniques to automate resume screening, candidate ranking, and intelligent job matching.

**Status**: ✅ Working On It Please Wait ...

### Dashboard Interface
![HireAssist Dashboard](docs/images/dashboard.png)


## 🚀 Key Features

### Core Functionality
- ✅ **AI-Powered Resume Parsing**: Extract structured data from PDF/DOCX resumes using spaCy NLP and LangChain
- ✅ **Dual Parser System**: NLP-based (Parser A) and Regex-based (Parser B) parsers for flexible extraction
- ✅ **Parser Performance Dashboard**: Real-time comparison of parsing accuracy and speed
- ✅ **Interactive Dashboard**: Modern React interface with real-time updates
- ✅ **API Status Monitoring**: Real-time health check indicator
- ✅ **Docker Support**: Complete containerization for development and production
- **Semantic Job Matching**: RAG-powered similarity search between resumes and job descriptions
- **Real-time Candidate Ranking**: Score and rank candidates using vector embeddings
- **Intelligent Screening**: Multi-criteria evaluation with customizable scoring algorithms

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
- **CI/CD Pipeline**: GitHub Actions automated testing and deployment

## 🛠 Tech Stack

### Frontend
- **React 18+** with TypeScript/JSX
- **Tailwind CSS** for responsive design
- **Vite** for fast build tooling
- **Chart.js** for analytics visualization
- **React Query** for data fetching
- **Lucide Icons** for UI components

### Backend
- **FastAPI** with Python 3.11+
- **PostgreSQL** for primary database
- **SQLAlchemy** ORM with Alembic migrations
- **Pydantic** for data validation
- **Uvicorn** ASGI server

### AI/ML Stack
- **spaCy** for NER and text processing
- **LangChain** for RAG implementation
- **OpenAI GPT-4** for text analysis (optional)
- **Pinecone/Qdrant** vector database
- **Sentence Transformers** for embeddings
- **FAISS** for local vector search

### DevOps & Infrastructure
- **Docker** containerization
- **Docker Compose** for development and production
- **GitHub Actions** CI/CD
- **Nginx** reverse proxy
- **PostgreSQL + Redis** with Docker
- **AWS/GCP** cloud deployment ready

## 📁 Project Structure

```
HireAssist/
├── frontend/                          # React Application
│   ├── src/
│   │   ├── __tests__/
│   │   │   └── App.test.tsx
│   │   ├── api/
│   │   │   └── resumeService.ts      # API service functions
│   │   ├── components/
│   │   │   ├── ApiStatus.tsx         # API health indicator
│   │   │   ├── ResumeUpload.jsx      # Resume upload component
│   │   │   └── ParserComparison/     # Parser comparison dashboard
│   │   │       ├── ComparisonCard.tsx
│   │   │       ├── ComparisonTable.tsx
│   │   │       ├── ParserComparisonDashboard.tsx
│   │   │       ├── PerformanceChart.tsx
│   │   │       └── index.ts
│   │   ├── hooks/
│   │   │   ├── useApiStatus.ts
│   │   │   └── useParserComparison.ts
│   │   ├── pages/
│   │   │   └── ParserComparisonPage.tsx
│   │   ├── types/
│   │   │   └── parser.ts
│   │   ├── App.css
│   │   ├── App.tsx
│   │   ├── index.css
│   │   └── main.tsx
│   ├── .dockerignore
│   ├── .env.example
│   ├── Dockerfile
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── vitest.config.ts
├── backend/                           # FastAPI Application
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       ├── jobs.py
│   │   │       ├── resumes.py
│   │   │       ├── screening.py
│   │   │       └── analytics.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # Settings from environment
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # Base model class
│   │   │   ├── candidate.py
│   │   │   ├── job.py
│   │   │   ├── organization.py
│   │   │   ├── resume.py
│   │   │   ├── screening.py
│   │   │   └── user.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── parser.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ai_service.py
│   │   │   ├── matching_service.py
│   │   │   ├── parser_nlp.py         # NLP parser (Parser A)
│   │   │   ├── parser_regex.py       # Regex parser (Parser B)
│   │   │   ├── rag_engine.py
│   │   │   ├── resume_parser.py
│   │   │   └── screening_service.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── validators.py
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── main.py                   # Entry point
│   ├── migrations/                   # Database migrations
│   │   ├── env.py                    # Auto-reads from .env
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_health.py
│   │   ├── test_parsers.py
│   │   └── test_screening.py
│   ├── .dockerignore
│   ├── .env.example
│   ├── Dockerfile
│   ├── alembic.ini                   # Alembic configuration (at backend root)
│   └── requirements.txt               # Cleaned Python dependencies
├── .github/
│   └── workflows/
│       └── ci.yml                   # GitHub Actions CI/CD
├── .env.example                      # Root environment template (Docker)
├── .gitignore
├── docker-compose.prod.yml           # Production setup with Nginx
├── docker-compose.yml                # Development setup
├── nginx.conf                        # Nginx reverse proxy config
├── docs/                            # Documentation
├── scripts/                         # Deployment scripts
└── README.md
```

## 🐳 Docker Setup

### Prerequisites
- Install [Docker](https://www.docker.com/products/docker-desktop)
- Install [Docker Compose](https://docs.docker.com/compose/install/)

### Quick Start - Docker Development

```bash
# 1. Clone repository
git clone https://github.com/AshminDhungana/HireAssist.git
cd HireAssist

# 2. Create .env file from template
cp .env.example .env

# 3. Start all services (PostgreSQL, Redis, Backend, Frontend)
docker-compose up -d

# 4. Wait for services to start (30 seconds)
sleep 30

# 5. Run database migrations
docker-compose exec backend alembic upgrade head

# 6. Access applications
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs

# 7. View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# 8. Stop services
docker-compose down
```

### Environment Variables Configuration

#### Root `.env` (docker-compose.yml reads this)
```env
# Database
DB_USER=hireassist
DB_PASSWORD=hireassist_dev_password
DB_NAME=hireassist_db
DATABASE_URL=postgresql://hireassist:hireassist_dev_password@postgres:5432/hireassist_db

# Redis
REDIS_URL=redis://redis:6379

# Security
SECRET_KEY=dev_secret_key_change_in_production

# API URLs
FRONTEND_API_URL=http://localhost:3000

# Debug
DEBUG=true
```

#### Backend `backend/.env` (local development)
```env
DATABASE_URL=postgresql://hireassist:hireassist_dev_password@localhost:5432/hireassist_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=dev_secret_key_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_FOLDER=./uploads
MAX_FILE_SIZE=10485760
OPENAI_API_KEY=
DEBUG=true
```

#### Frontend `frontend/.env.local` (local development)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=HireAssist
VITE_DEBUG=true
```

### Database Migrations with Alembic

**Key Point**: Alembic configuration (`alembic.ini`) is at `backend/alembic.ini` (backend root level)

**Automatic Configuration**: `migrations/env.py` reads database URL from `.env` automatically!

```bash
# Create new migration (auto-detects schema changes)
docker-compose exec backend alembic revision --autogenerate -m "Add users table"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback one migration
docker-compose exec backend alembic downgrade -1

# View current revision
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history
```

**How it works:**
1. `migrations/env.py` reads `DATABASE_URL` from `.env`
2. Configuration is automatic - no manual editing needed
3. Works seamlessly in Docker and local development

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
    embedding VECTOR(1536),
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
    parsed_data JSONB,
    raw_text TEXT,
    embedding VECTOR(1536),
    skills TEXT[],
    experience_years INTEGER,
    education_level VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Job Applications
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    candidate_id UUID REFERENCES candidates(id),
    resume_id UUID REFERENCES resumes(id),
    status VARCHAR(50) DEFAULT 'submitted',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Screening Results
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

**Note:** This schema requires PostgreSQL with the `pgvector` extension enabled.

## 🚀 Deployment Guide

### Local Development (Without Docker)

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Create .env
cp .env.example .env

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### Docker Development

```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Stop services
docker-compose down
```

### Production Deployment

```bash
# Create production .env
cp .env.example .env
# Edit .env with production values

# Build and deploy
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 API Documentation

### Health Check
```
GET /api/v1/health
Response: { "status": "healthy", "message": "API is running" }
```

### Authentication Endpoints
```
POST /api/v1/auth/login
POST /api/v1/auth/register
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
```

### Resume Management
```
POST /api/v1/resumes/upload
GET  /api/v1/resumes/{id}
PUT  /api/v1/resumes/{id}
DELETE /api/v1/resumes/{id}
```

### Job Management
```
POST /api/v1/jobs
GET  /api/v1/jobs
GET  /api/v1/jobs/{id}
PUT  /api/v1/jobs/{id}
DELETE /api/v1/jobs/{id}
```

### Screening & Matching
```
POST /api/v1/screening/match
GET  /api/v1/screening/results
POST /api/v1/screening/bulk
```

## 🧪 Testing

### Backend Testing
```bash
docker-compose exec backend pytest tests/ -v
```

### Frontend Testing
```bash
cd frontend
npm test
```

## ✨ Current Implementation Status

### 📋 In Progress
- Resume parsing API endpoints
- File upload handling
- Database integration

### 🔜 Planned
- Advanced job matching algorithm
- Vector database integration
- Multi-tenant support
- Advanced analytics dashboard
- Mobile app

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models and embeddings
- LangChain for RAG framework
- FastAPI for the excellent web framework
- React team for the frontend framework
- spaCy for NLP capabilities
- Docker for containerization

---

**Built with ❤️ for modern recruitment workflows**

**Current Version**: 1.0.0 (Tasks 14-16 Complete)  
**Last Updated**: October 31, 2025  
**Status**: 🟢 Development Active
