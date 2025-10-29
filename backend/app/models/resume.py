from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
import uuid
from app.core.database import Base
# If using pgvector
from pgvector.sqlalchemy import Vector

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    parsed_data = Column(JSONB)
    raw_text = Column(Text)
    embedding = Column(Vector(1536))  # Requires pgvector extension and package
    skills = Column(ARRAY(Text))      # Native PostgreSQL array of text
    experience_years = Column(Integer)
    education_level = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
