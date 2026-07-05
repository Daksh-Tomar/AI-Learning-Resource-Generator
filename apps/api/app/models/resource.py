from sqlalchemy import Column, String, DateTime, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base

class ResourceModel(Base):
    __tablename__ = "resources"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    creator_name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    language = Column(String, nullable=True)
    processing_status = Column(String, default="PENDING")
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('provider', 'external_id', name='uq_provider_external_id'),
    )
