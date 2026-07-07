from sqlalchemy import Column, String, DateTime, ForeignKey, Float, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSON
import uuid
from datetime import datetime
from app.core.database import Base

class ResourceDifficultyProfileModel(Base):
    __tablename__ = "resource_difficulty_profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False)
    estimated_level = Column(String, nullable=False)
    confidence = Column(Float, nullable=True)
    feature_values = Column(JSON, nullable=False)
    feature_extractor_version = Column(String, nullable=False)
    estimator_version = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('resource_id', 'estimator_version', name='uq_difficulty_resource_estimator'),
    )

class ResourceFeatureEvidenceModel(Base):
    __tablename__ = "resource_feature_evidence"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False)
    feature_name = Column(String, nullable=False)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("transcript_chunks.id", ondelete="CASCADE"), nullable=False)
    evidence_score = Column(Float, nullable=True)
    extractor_version = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
