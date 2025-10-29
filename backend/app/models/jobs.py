from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.dialects.postgresql import TEXT, INT4RANGE
from pgvector.sqlalchemy import Vector  # Requires pgvector if using embeddings
import uuid
from sqlalchemy.sql import func
from app.core.database import Base

class Job(Base):
    __tablename__ = "jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text)
    location = Column(String(255))
    salary_range = Column(INT4RANGE)
    status = Column(String(50), server_default="active")
    embedding = Column(Vector(1536))      # Requires pgvector extension
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
