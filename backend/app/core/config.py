from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Secrets (optional in local dev)
    OPENAI_API_KEY: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    DATABASE_URL: Optional[str] = None

    # Vector DB selection: 'inmemory' | 'pinecone' | 'qdrant'
    VECTOR_BACKEND: str = "inmemory"

    # Pinecone
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX: Optional[str] = None

    # Qdrant
    QDRANT_URL: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = None

    # CORS & Security
    ALLOW_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://localhost:3001"
    RATE_LIMIT_PER_MINUTE: int = 120

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
