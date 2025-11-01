from sqlalchemy import Column, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from sqlalchemy.sql import func
from app.core.database import Base

class ScreeningResult(Base):
    __tablename__ = "screening_results"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True),  nullable=True)
    overall_score = Column(Numeric(5, 2))
    skill_match_score = Column(Numeric(5, 2))
    experience_score = Column(Numeric(5, 2))
    education_score = Column(Numeric(5, 2))
    detailed_analysis = Column(JSONB)
    created_at = Column(DateTime, server_default=func.now())
