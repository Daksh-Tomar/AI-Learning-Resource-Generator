from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid
from datetime import datetime
from app.core.database import Base

class LearnerProfileModel(Base):
    __tablename__ = "learner_profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    subject = Column(String, nullable=False)
    goal = Column(String, nullable=False)
    current_level = Column(String, nullable=False)
    target_level = Column(String, nullable=True)
    deadline_days = Column(Integer, nullable=False)
    daily_hours = Column(Float, nullable=False)
    preferred_language = Column(String, nullable=True)
    wants_projects = Column(Boolean, default=False)
    wants_interview_prep = Column(Boolean, default=False)
    
    # Store lists as JSON for SQLite compatibility, or ARRAY if strict PG
    known_topics = Column(JSON, default=list)
    weak_topics = Column(JSON, default=list)
    preferred_formats = Column(JSON, default=list)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
