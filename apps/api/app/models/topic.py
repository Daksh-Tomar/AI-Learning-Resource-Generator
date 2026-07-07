from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base

class TopicModel(Base):
    __tablename__ = "topics"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    canonical_name = Column(String, nullable=False)
    normalized_name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class TopicAliasModel(Base):
    __tablename__ = "topic_aliases"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    alias = Column(String, nullable=False)
    normalized_alias = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class ResourceTopicModel(Base):
    __tablename__ = "resource_topics"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    confidence = Column(Float, nullable=True)
    coverage_status = Column(String, nullable=False) # e.g. STRONG, MODERATE, WEAK
    evidence_seconds = Column(Float, nullable=True)
    extraction_version = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('resource_id', 'topic_id', 'extraction_version', name='uq_resource_topic_version'),
    )

class ResourceTopicEvidenceModel(Base):
    __tablename__ = "resource_topic_evidence"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_topic_id = Column(UUID(as_uuid=True), ForeignKey("resource_topics.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("transcript_chunks.id", ondelete="CASCADE"), nullable=False)
    evidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('resource_topic_id', 'chunk_id', name='uq_topic_evidence_chunk'),
    )
