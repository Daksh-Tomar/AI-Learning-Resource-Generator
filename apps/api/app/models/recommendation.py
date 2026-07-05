from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base

class RecommendationSession(Base):
    __tablename__ = "recommendation_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    search_session_id = Column(UUID(as_uuid=True), ForeignKey("search_sessions.id"), nullable=False)
    status = Column(String, default="PENDING")
    algorithm_version = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class RecommendationModel(Base):
    __tablename__ = "recommendations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_session_id = Column(UUID(as_uuid=True), ForeignKey("recommendation_sessions.id"), nullable=False)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id"), nullable=False)
    rank = Column(Integer, nullable=False)
    category = Column(String, nullable=True)
    final_score = Column(Float, nullable=False)
    score_breakdown = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
