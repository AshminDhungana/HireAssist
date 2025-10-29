from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
from app.core.database import Base

class Application(Base):
    __tablename__ = "applications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"))
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"))
    status = Column(String(50), server_default="submitted")
    applied_at = Column(DateTime, server_default=func.now())
