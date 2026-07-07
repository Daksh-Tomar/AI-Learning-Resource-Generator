from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime
from app.core.database import Base

class ChunkEmbeddingModel(Base):
    __tablename__ = "chunk_embeddings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("transcript_chunks.id", ondelete="CASCADE"), nullable=False)
    model_name = Column(String, nullable=False)
    model_version = Column(String, nullable=False)
    embedding_dimension = Column(Integer, nullable=False)
    embedding = Column(Vector(1536), nullable=False) # Will use dynamic size mapping in Alembic if needed
    content_hash = Column(String, nullable=False)
    embedded_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('chunk_id', 'model_name', 'model_version', name='uq_chunk_embedding_model_version'),
    )
