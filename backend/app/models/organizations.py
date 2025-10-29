from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from sqlalchemy.sql import func
from app.core.database import Base

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    domain = Column(String(100))
    settings = Column(JSONB)
    created_at = Column(DateTime, server_default=func.now())
