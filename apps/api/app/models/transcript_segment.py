from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base

class TranscriptSegmentModel(Base):
    __tablename__ = "transcript_segments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transcript_id = Column(UUID(as_uuid=True), ForeignKey("transcripts.id"), nullable=False)
    segment_index = Column(Integer, nullable=False)
    start_seconds = Column(Float, nullable=False)
    duration_seconds = Column(Float, nullable=False)
    text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('transcript_id', 'segment_index', name='uq_transcript_segment_index'),
    )
