# HireAssist - AI-Powered Resume Screening and Parsing System

## Overview

This system is a **comprehensive, production-ready Resume/CV Screening and Parsing System** built with modern technologies including **React**, **Tailwind CSS**, **Python FastAPI**, **RAG (Retrieval-Augmented Generation)**, and **LangChain**. The system leverages advanced AI techniques to automate resume screening, candidate ranking, and intelligent job matching.

**Status**: ✅ **ACTIVE DEVELOPMENT** - Core features working, system operational

### Dashboard Interface
![HireAssist Dashboard](docs/images/dashboard.png)

---

## 🚀 Key Features

### ✅ Currently Working Features
- **AI-Powered Resume Parsing**: Extract structured data from PDF/DOCX resumes using spaCy NLP
- **Resume Upload & Storage**: Secure file upload with candidate profile linking
- **Dual Parser System**: NLP-based and Regex-based parsers for flexible extraction
- **Interactive Dashboard**: Modern React interface with real-time updates
- **API Status Monitoring**: Real-time health check indicator
- **Docker Support**: Complete containerization for development and production
- **Authentication System**: JWT-based login with role-based access control
- **Database Integration**: PostgreSQL with complete schema for candidates, resumes, jobs

### 🔜 In Development / Planned
- **Semantic Job Matching**: RAG-powered similarity search between resumes and job descriptions
- **Real-time Candidate Ranking**: Score and rank candidates using vector embeddings
- **Intelligent Screening**: Multi-criteria evaluation with customizable scoring algorithms
- **Vector Database Integration**: Pinecone/Qdrant for scalable semantic search
- **Hybrid Search**: Combines keyword-based and semantic matching
- **Entity Recognition**: Advanced skills extraction using spaCy NER
- **Adaptive Retrieval**: RAG Fusion for complex job requirement queries
- **Conversation AI**: Chat interface for querying candidate database
- **Multi-tenant Architecture**: Support for multiple organizations
- **Analytics Dashboard**: Comprehensive recruitment metrics and insights
- **CI/CD Pipeline**: GitHub Actions automated testing and deployment

---

## 🛠 Tech Stack

### Frontend
- **React 18+** with TypeScript/JSX
- **Tailwind CSS** for responsive design
- **Vite** for fast build tooling
- **Axios** for API communication
- **React Query** for data fetching (optional)
- **Lucide Icons** for UI components

### Backend
- **FastAPI** with Python 3.13+
- **PostgreSQL** for primary database
- **SQLAlchemy** ORM with async support
- **Pydantic** for data validation
- **Uvicorn** ASGI server
- **spaCy** for NLP and text processing

### AI/ML Stack
- **spaCy** for NER and text processing
- **LangChain** for RAG implementation (framework ready)
- **OpenAI GPT-4** for text analysis (optional)
- **Sentence Transformers** for embeddings (optional)

### DevOps & Infrastructure
- **Docker** containerization
- **Docker Compose** for development and production
- **Nginx** reverse proxy
- **PostgreSQL** with Docker
- **AWS/GCP** cloud deployment ready

---

## 📁 Project Structure

```
HireAssist/
├── frontend/                          # React Application
│   ├── src/
│   │   ├── api/
│   │   │   ├── resumeService.ts      # Resume API service
│   │   │   ├── authService.ts        # Authentication service
│   │   │   └── apiClient.ts          # Axios instance
│   │   ├── components/
│   │   │   ├── ResumeUpload.tsx      # Resume upload component
│   │   │   ├── ApiStatus.tsx         # API health indicator
│   │   │   └── AuthForm.tsx          # Login/Register form
│   │   ├── hooks/
│   │   │   ├── useApiStatus.ts
│   │   │   └── useAuth.ts
│   │   ├── pages/
│   │   │   ├── AuthPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── ResumeManagementPage.tsx
│   │   │   └── JobManagementPage.tsx
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── .env.example
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── backend/                           # FastAPI Application
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # Authentication endpoints
│   │   │   ├── resumes.py            # Resume upload/parse endpoints
│   │   │   ├── candidates.py         # Candidate management
│   │   │   ├── jobs.py               # Job management
│   │   │   ├── matching.py           # Job matching endpoints
│   │   │   ├── health.py             # Health check
│   │   │   └── admin.py              # Admin endpoints
│   │   ├── core/
│   │   │   ├── config.py             # Settings from environment
│   │   │   ├── database.py           # Database connection
│   │   │   ├── security.py           # JWT and auth
│   │   │   └── middleware.py         # Error handling
│   │   ├── models/
│   │   │   ├── users.py              # User model
│   │   │   ├── candidate.py          # Candidate profile
│   │   │   ├── resume.py             # Resume storage
│   │   │   ├── jobs.py               # Job postings
│   │   │   ├── applications.py       # Job applications
│   │   │   └── screening_results.py  # Screening scores
│   │   ├── schemas/
│   │   │   ├── auth.py               # Auth schemas
│   │   │   └── resumes.py            # Resume schemas
│   │   ├── services/
│   │   │   ├── resumeparser.py       # Resume parsing logic
│   │   │   ├── rag_resume_parser.py  # RAG parser (framework)
│   │   │   └── skills.json           # Skills database
│   │   └── main.py                   # Entry point
│   │
│   ├── migrations/                   # Alembic database migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │
│   ├── tests/
│   │   ├── test_health.py
│   │   ├── test_resume_parser.py
│   │   └── test_integration_upload_parse.py
│   │
│   ├── uploads/                      # Resume file storage
│   ├── .env.example
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── requirements.txt
│   └── requirements-dev.txt
│
├── .github/workflows/ci.yml           # GitHub Actions CI/CD
├── docker-compose.yml                 # Development setup
├── docker-compose.prod.yml            # Production setup
├── nginx.conf                         # Nginx configuration
├── .env.example                       # Root environment template
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Docker Desktop** (recommended) or Python 3.13+ & Node.js 18+
- **PostgreSQL** (if running locally without Docker)
- **Git**

### 🐳 Docker Quick Start (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/AshminDhungana/HireAssist.git
cd HireAssist

# 2. Create environment file
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Wait for services to start
sleep 30

# 5. Access applications
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/api/docs

# 6. Login with default credentials
# Email: admin@hireassist.com
# Password: AdminPassword123!
```

### 🖥️ Local Development (Without Docker)

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Create .env file
cp .env.example .env

# Run database migrations
alembic upgrade head
(Change sqlalchemy.url in alembic.ini if necessary)

# Start backend server
uvicorn app.main:app --reload
# Server runs on http://localhost:8000
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env.local

# Start development server
npm run dev
# Application runs on http://localhost:5173
```

---

## 🔑 Environment Variables

### Root `.env` (Docker)
```env
# Database Configuration
DB_USER=hireassist
DB_PASSWORD=secure_password_here
DB_NAME=hireassist_db
DATABASE_URL=postgresql://hireassist:secure_password_here@postgres:5432/hireassist_db

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Debug Mode
DEBUG=false

# Redis (optional)
REDIS_URL=redis://redis:6379
```

### Backend `backend/.env` (Local Development)
```env
# Database
DATABASE_URL=postgresql://hireassist:password@localhost:5432/hireassist_db

# Security
SECRET_KEY=dev_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload
UPLOAD_FOLDER=./uploads
MAX_FILE_SIZE=10485760

# OpenAI (optional)
OPENAI_API_KEY=sk-your-key-here

# Debug
DEBUG=true
```

### Frontend `frontend/.env.local` (Local Development)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=HireAssist
VITE_DEBUG=true
```

---

## 🗄️ Database Schema

The system uses PostgreSQL with the following core tables:

### Users & Authentication
```sql
users (id, email, password_hash, role, is_approved, created_at)
```

### Candidates & Resumes
```sql
candidates (id, user_id, name, email, phone, location, summary, created_at)
resumes (id, candidate_id, filename, file_path, parsed_data, skills, experience_years, education_level, created_at)
```

### Jobs & Applications
```sql
jobs (id, organization_id, title, description, requirements, location, status, created_at)
applications (id, job_id, candidate_id, resume_id, status, applied_at)
```

### Screening Results
```sql
screening_results (id, application_id, overall_score, skill_match_score, experience_score, detailed_analysis, created_at)
```

**Database Migrations** are managed with **Alembic** and run automatically on startup.

---

## 📊 API Documentation

### Authentication Endpoints
```
POST   /api/v1/auth/register         # Register new user
POST   /api/v1/auth/login            # Login (returns JWT token)
POST   /api/v1/auth/refresh          # Refresh token
POST   /api/v1/auth/logout           # Logout
```

### Resume Management
```
POST   /api/v1/resumes/upload        # Upload resume (requires auth)
GET    /api/v1/resumes/list          # List user's resumes
GET    /api/v1/resumes/{id}/details  # Get resume details
POST   /api/v1/resumes/{id}/parse    # Parse resume
DELETE /api/v1/resumes/{id}          # Delete resume
```

### Candidate Management
```
GET    /api/v1/candidates            # List candidates
POST   /api/v1/candidates            # Create candidate profile
GET    /api/v1/candidates/{id}       # Get candidate details
PUT    /api/v1/candidates/{id}       # Update candidate
```

### Job Management
```
POST   /api/v1/jobs                  # Create job posting
GET    /api/v1/jobs                  # List all jobs
GET    /api/v1/jobs/{id}             # Get job details
PUT    /api/v1/jobs/{id}             # Update job
DELETE /api/v1/jobs/{id}             # Delete job
```

### Health & Status
```
GET    /api/v1/health                # API health check
GET    /                              # Root endpoint
```

**Full API documentation available at**: `http://localhost:8000/api/docs` (Swagger UI)

---

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_resume_parser.py -v

# Run with coverage
pytest tests/ --cov=app
```

### Frontend Tests
```bash
cd frontend

# Run tests
npm test

# Watch mode
npm test -- --watch
```

---

## 🚀 Deployment

### Docker Production Deployment
```bash
# Build production images
docker build -t hireassist-backend ./backend
docker build -t hireassist-frontend ./frontend

# Deploy with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

### Cloud Deployment (AWS Example)
```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag hireassist-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/hireassist-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/hireassist-backend:latest
```

---

## 📋 Current Implementation Status

### ✅ Completed Features (November 2025)
- User authentication and JWT tokens
- Resume upload and storage
- Resume parsing with spaCy
- Database schema and migrations
- API endpoints for all core functionality
- Docker containerization
- Frontend login page
- Resume upload component
- Admin dashboard foundation

### 🔄 In Progress
- Resume parsing refinement
- Frontend dashboard pages
- Job matching algorithm
- Candidate ranking system

### 🔜 Next Phase (Planned)
- Vector database integration (Pinecone/Qdrant)
- Advanced semantic matching
- RAG implementation
- Multi-tenant support
- Analytics dashboard
- Mobile app
- Advanced filtering and search

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Code Standards
- Use **TypeScript** for frontend
- Follow **PEP 8** for backend Python
- Write tests for new features
- Update documentation accordingly

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review documentation in `/docs`

---

## 📄 License

This project is licensed under the **MIT License** - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework
- **React** - Frontend library
- **spaCy** - NLP capabilities
- **SQLAlchemy** - ORM framework
- **LangChain** - RAG framework
- **Docker** - Containerization
- **PostgreSQL** - Database
- Open-source community

---

## 📈 Project Roadmap

| Phase | Timeline | Features |
|-------|----------|----------|
| **Phase 1** | ✅ Complete | Core APIs, Auth, Resume Upload |
| **Phase 2** | 🔄 In Progress | Resume Parsing, Dashboard UI |
| **Phase 3** | 🔜 Q4 2025 | Job Matching, Vector DB |
| **Phase 4** | 🔜 Q1 2026 | Multi-tenant, Analytics |
| **Phase 5** | 🔜 Q2 2026 | Mobile App, Advanced AI |

---

**Built with ❤️ for modern recruitment workflows**

**Current Version**: 1.0.0  
**Last Updated**: November 1, 2025  
**Status**: 🟢 Active Development

---

### Quick Links
- 📖 [Technical Documentation](./docs/technical-docs.md)
- 🚀 [Frontend Deployment Guide](./docs/frontend-deployment.md)
- 💻 [Implementation Code](./docs/implementation-code.md)
- 📋 [Implementation Roadmap](./docs/implementation_roadmap.json)
