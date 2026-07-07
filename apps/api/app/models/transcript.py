from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime
from app.core.database import Base

class TranscriptModel(Base):
    __tablename__ = "transcripts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id"), nullable=False)
    language = Column(String, nullable=True)
    source_type = Column(String, nullable=True)
    full_text = Column(String, nullable=True)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class TranscriptChunkModel(Base):
    __tablename__ = "transcript_chunks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transcript_id = Column(UUID(as_uuid=True), ForeignKey("transcripts.id"), nullable=False)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(String, nullable=False)
    start_seconds = Column(Float, nullable=True)
    end_seconds = Column(Float, nullable=True)
    start_segment_index = Column(Integer, nullable=True)
    end_segment_index = Column(Integer, nullable=True)
    token_count = Column(Integer, nullable=True)
    chunking_version = Column(String, nullable=False)
    chunking_config_hash = Column(String, nullable=False)
    content_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('transcript_id', 'chunking_version', 'chunking_config_hash', 'chunk_index', name='uq_chunk_version_index'),
    )
