# Frontend Implementation & Deployment Guide

## Frontend Implementation

### 1. React Project Setup with TypeScript and Tailwind

```typescript
// frontend/src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import { store } from './store'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </QueryClientProvider>
    </Provider>
  </React.StrictMode>,
)
```

### 2. API Service Layer

```typescript
// frontend/src/services/api.ts
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

class APIService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config
        
        // Handle token refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true
          
          try {
            const refreshToken = localStorage.getItem('refresh_token')
            const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
              refresh_token: refreshToken,
            })
            
            const { access_token, refresh_token } = response.data
            localStorage.setItem('access_token', access_token)
            localStorage.setItem('refresh_token', refresh_token)
            
            return this.client(originalRequest)
          } catch (refreshError) {
            // Redirect to login if refresh fails
            localStorage.clear()
            window.location.href = '/login'
            return Promise.reject(refreshError)
          }
        }
        
        return Promise.reject(error)
      }
    )
  }

  // Auth methods
  async login(email: string, password: string) {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)
    
    const response = await this.client.post('/api/v1/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  }

  async register(userData: any) {
    const response = await this.client.post('/api/v1/auth/register', userData)
    return response.data
  }

  // Resume methods
  async uploadResume(file: File, jobId?: string) {
    const formData = new FormData()
    formData.append('file', file)
    if (jobId) formData.append('job_id', jobId)
    
    const response = await this.client.post('/api/v1/resumes/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  }

  async getResumes(params?: any) {
    const response = await this.client.get('/api/v1/resumes', { params })
    return response.data
  }

  async getResumeById(id: string) {
    const response = await this.client.get(`/api/v1/resumes/${id}`)
    return response.data
  }

  async parseResume(id: string) {
    const response = await this.client.post(`/api/v1/resumes/${id}/parse`)
    return response.data
  }

  // Job methods
  async createJob(jobData: any) {
    const response = await this.client.post('/api/v1/jobs', jobData)
    return response.data
  }

  async getJobs(params?: any) {
    const response = await this.client.get('/api/v1/jobs', { params })
    return response.data
  }

  async getJobById(id: string) {
    const response = await this.client.get(`/api/v1/jobs/${id}`)
    return response.data
  }

  // Screening methods
  async matchCandidates(jobId: string, filters?: any) {
    const response = await this.client.post(`/api/v1/screening/match`, {
      job_id: jobId,
      filters,
    })
    return response.data
  }

  async getScreeningResults(applicationId: string) {
    const response = await this.client.get(`/api/v1/screening/results/${applicationId}`)
    return response.data
  }

  // Analytics methods
  async getAnalytics(params?: any) {
    const response = await this.client.get('/api/v1/analytics', { params })
    return response.data
  }
}

export const apiService = new APIService()
```

### 3. Resume Upload Component

```typescript
// frontend/src/components/ResumeUpload.tsx
import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiService } from '../services/api'
import { toast } from 'react-hot-toast'

export const ResumeUpload: React.FC = () => {
  const [uploadProgress, setUploadProgress] = useState(0)
  const queryClient = useQueryClient()

  const uploadMutation = useMutation({
    mutationFn: (file: File) => apiService.uploadResume(file),
    onSuccess: (data) => {
      toast.success('Resume uploaded successfully!')
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
      setUploadProgress(0)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to upload resume')
      setUploadProgress(0)
    },
  })

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      uploadMutation.mutate(file)
    }
  }, [uploadMutation])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: false,
  })

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
          transition-colors duration-200
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
        `}
      >
        <input {...getInputProps()} />
        
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          stroke="currentColor"
          fill="none"
          viewBox="0 0 48 48"
        >
          <path
            d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        
        <div className="mt-4">
          {isDragActive ? (
            <p className="text-lg text-blue-600">Drop the resume here...</p>
          ) : (
            <>
              <p className="text-lg text-gray-700">
                Drag and drop your resume here, or click to select
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Supports PDF and DOCX files up to 10MB
              </p>
            </>
          )}
        </div>
      </div>

      {uploadMutation.isPending && (
        <div className="mt-4">
          <div className="relative pt-1">
            <div className="flex mb-2 items-center justify-between">
              <span className="text-sm font-semibold text-blue-700">
                Uploading...
              </span>
            </div>
            <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-blue-200">
              <div
                style={{ width: `${uploadProgress}%` }}
                className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500 transition-all duration-300"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
```

### 4. Candidate Matching Dashboard

```typescript
// frontend/src/components/CandidateMatching.tsx
import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiService } from '../services/api'

interface CandidateMatch {
  resume_id: string
  overall_score: number
  breakdown: {
    skill_match: number
    experience_match: number
    education_match: number
  }
  matched_skills: string[]
  missing_skills: string[]
}

export const CandidateMatching: React.FC<{ jobId: string }> = ({ jobId }) => {
  const [filters, setFilters] = useState({
    min_score: 60,
    min_experience: 0,
  })

  const { data: matches, isLoading } = useQuery({
    queryKey: ['matches', jobId, filters],
    queryFn: () => apiService.matchCandidates(jobId, filters),
  })

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100'
    if (score >= 60) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Candidate Matches</h2>
        <p className="text-gray-600">Showing top {matches?.matches?.length || 0} candidates</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Minimum Score
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={filters.min_score}
              onChange={(e) => setFilters({ ...filters, min_score: Number(e.target.value) })}
              className="w-full"
            />
            <span className="text-sm text-gray-600">{filters.min_score}%</span>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Minimum Experience (years)
            </label>
            <input
              type="number"
              min="0"
              value={filters.min_experience}
              onChange={(e) => setFilters({ ...filters, min_experience: Number(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
        </div>
      </div>

      {/* Candidate List */}
      <div className="space-y-4">
        {matches?.matches?.map((match: CandidateMatch, index: number) => (
          <div
            key={match.resume_id}
            className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0">
                  <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                    <span className="text-xl font-bold text-blue-600">#{index + 1}</span>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    Candidate {match.resume_id.slice(0, 8)}
                  </h3>
                </div>
              </div>

              <div className={`px-4 py-2 rounded-full font-semibold ${getScoreColor(match.overall_score)}`}>
                {match.overall_score}% Match
              </div>
            </div>

            {/* Score Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <div className="text-sm text-gray-600 mb-1">Skill Match</div>
                <div className="flex items-center">
                  <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${match.breakdown.skill_match}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold">{match.breakdown.skill_match}%</span>
                </div>
              </div>

              <div>
                <div className="text-sm text-gray-600 mb-1">Experience</div>
                <div className="flex items-center">
                  <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${match.breakdown.experience_match}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold">{match.breakdown.experience_match}%</span>
                </div>
              </div>

              <div>
                <div className="text-sm text-gray-600 mb-1">Education</div>
                <div className="flex items-center">
                  <div className="flex-1 bg-gray-200 rounded-full h-2 mr-2">
                    <div
                      className="bg-purple-600 h-2 rounded-full"
                      style={{ width: `${match.breakdown.education_match}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold">{match.breakdown.education_match}%</span>
                </div>
              </div>
            </div>

            {/* Skills */}
            <div className="space-y-2">
              {match.matched_skills.length > 0 && (
                <div>
                  <span className="text-sm font-medium text-gray-700">Matching Skills: </span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {match.matched_skills.map((skill) => (
                      <span
                        key={skill}
                        className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {match.missing_skills.length > 0 && (
                <div>
                  <span className="text-sm font-medium text-gray-700">Missing Skills: </span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {match.missing_skills.map((skill) => (
                      <span
                        key={skill}
                        className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded-full"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="mt-4 flex space-x-2">
              <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                View Details
              </button>
              <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300">
                Schedule Interview
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

## Deployment Guide

### 1. Docker Compose for Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: resume_user
      POSTGRES_PASSWORD: resume_password
      POSTGRES_DB: resume_screening
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U resume_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://resume_user:resume_password@postgres:5432/resume_screening
      REDIS_URL: redis://redis:6379
      SECRET_KEY: ${SECRET_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      PINECONE_API_KEY: ${PINECONE_API_KEY}
      PINECONE_ENVIRONMENT: ${PINECONE_ENVIRONMENT}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - uploads:/app/uploads
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      VITE_API_BASE_URL: http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:
  uploads:
```

### 2. Production Dockerfile (Backend)

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Make sure scripts are executable
RUN chmod +x /app/scripts/*.sh

# Set PATH
ENV PATH=/root/.local/bin:$PATH

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### 3. Production Dockerfile (Frontend)

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application files
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 4. GitHub Actions CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Cache pip packages
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        run: |
          cd backend
          pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  test-frontend:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Cache node modules
        uses: actions/cache@v3
        with:
          path: frontend/node_modules
          key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run tests
        run: |
          cd frontend
          npm run test
      
      - name: Build
        run: |
          cd frontend
          npm run build

  deploy:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        env:
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
          SERVER_HOST: ${{ secrets.SERVER_HOST }}
        run: |
          echo "$DEPLOY_KEY" > deploy_key
          chmod 600 deploy_key
          ssh -i deploy_key -o StrictHostKeyChecking=no user@$SERVER_HOST '
            cd /app/resume-screening-system &&
            git pull origin main &&
            docker-compose -f docker-compose.prod.yml up -d --build
          '
```

### 5. Environment Configuration Template

```bash
# .env.example
# Application
APP_NAME="Resume Screening System"
DEBUG=False
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/resume_screening

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
ALLOWED_HOSTS=localhost,yourdomain.com

# File Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# AI Services
OPENAI_API_KEY=your-openai-api-key
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=resume-screening

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 6. Deployment Checklist

- [ ] Set up production database (PostgreSQL)
- [ ] Configure Redis for caching
- [ ] Set up vector database (Pinecone/Qdrant)
- [ ] Configure environment variables
- [ ] Set up SSL certificates (Let's Encrypt)
- [ ] Configure domain and DNS
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure logging (ELK Stack)
- [ ] Set up backup strategy
- [ ] Configure CI/CD pipeline
- [ ] Perform security audit
- [ ] Load testing
- [ ] Create rollback plan
- [ ] Document deployment procedures

---

This comprehensive guide provides everything needed to build and deploy a production-ready Resume Screening System with modern technologies and best practices.