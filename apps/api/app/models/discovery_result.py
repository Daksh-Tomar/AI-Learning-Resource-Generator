from sqlalchemy import Column, DateTime, ForeignKey, Integer, Float, UniqueConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base

class DiscoveryResultModel(Base):
    __tablename__ = "discovery_results"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    search_session_id = Column(UUID(as_uuid=True), ForeignKey("search_sessions.id"), nullable=False)
    search_query_id = Column(UUID(as_uuid=True), ForeignKey("search_queries.id"), nullable=False)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id"), nullable=False)
    provider_rank = Column(Integer, nullable=True)
    selected_for_ingestion = Column(Boolean, default=False)
    ingestion_priority_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('search_query_id', 'resource_id', name='uq_discovery_query_resource'),
    )
