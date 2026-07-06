from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base

class CommentCollectionBatchModel(Base):
    __tablename__ = "comment_collection_batches"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id"), nullable=False)
    provider = Column(String, nullable=False)
    sampling_strategy = Column(String, nullable=True)
    requested_limit = Column(Integer, default=0)
    actual_count = Column(Integer, default=0)
    order_mode = Column(String, nullable=True)
    collected_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class CommentModel(Base):
    __tablename__ = "comments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id = Column(UUID(as_uuid=True), ForeignKey("resources.id"), nullable=False)
    collection_batch_id = Column(UUID(as_uuid=True), ForeignKey("comment_collection_batches.id"), nullable=True)
    external_comment_id = Column(String, nullable=False)
    text = Column(String, nullable=False)
    like_count = Column(Integer, default=0)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('external_comment_id', name='uq_comments_external_id'),
    )

