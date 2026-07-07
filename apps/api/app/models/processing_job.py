from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base

class ProcessingJobModel(Base):
    __tablename__ = "processing_jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False)
    search_session_id = Column(UUID(as_uuid=True), ForeignKey("search_sessions.id", ondelete="SET NULL"), nullable=True)
    job_type = Column(String, nullable=False) # e.g. TRANSCRIPT_PREPROCESSING, CHUNKING, EMBEDDING, TOPIC_EXTRACTION
    status = Column(String, default="PENDING")
    algorithm_version = Column(String, nullable=True)
    model_name = Column(String, nullable=True)
    model_version = Column(String, nullable=True)
    attempt_count = Column(Integer, default=0)
    error_code = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
