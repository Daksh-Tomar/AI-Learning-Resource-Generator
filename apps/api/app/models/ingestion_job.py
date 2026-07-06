from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base

class IngestionJobModel(Base):
    __tablename__ = "ingestion_jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    search_session_id = Column(UUID(as_uuid=True), ForeignKey("search_sessions.id"), nullable=False)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id"), nullable=False)
    job_type = Column(String, nullable=False) # METADATA, TRANSCRIPT, COMMENTS, METRICS
    status = Column(String, default="PENDING")
    attempt_count = Column(Integer, default=0)
    error_code = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
