from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base

class SearchSession(Base):
    __tablename__ = "search_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learner_profile_id = Column(UUID(as_uuid=True), ForeignKey("learner_profiles.id"), nullable=False)
    status = Column(String, default="CREATED")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class SearchPlanModel(Base):
    __tablename__ = "search_plans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    search_session_id = Column(UUID(as_uuid=True), ForeignKey("search_sessions.id"), nullable=False)
    primary_topic = Column(String, nullable=False)
    search_queries = Column(JSON, default=list)
    required_concepts = Column(JSON, default=list)
    project_queries = Column(JSON, default=list)
    interview_queries = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
