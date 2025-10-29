from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    SECRET_KEY: str
    DATABASE_URL: str
    PINECONE_ENVIRONMENT: str
    # Add other config vars as needed

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
