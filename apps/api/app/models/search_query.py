from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base

class SearchQueryModel(Base):
    __tablename__ = "search_queries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    search_session_id = Column(UUID(as_uuid=True), ForeignKey("search_sessions.id"), nullable=False)
    query_text = Column(String, nullable=False)
    query_type = Column(String, nullable=False)
    execution_status = Column(String, default="PENDING")
    provider = Column(String, nullable=True)
    result_count = Column(Integer, default=0)
    error_code = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
