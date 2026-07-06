from sqlalchemy.orm import Session
from sqlalchemy import select, update
from typing import List, Optional
from uuid import UUID
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.transcript import TranscriptModel
from app.models.transcript_segment import TranscriptSegmentModel

class TranscriptRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_resource_id(self, resource_id: UUID) -> Optional[TranscriptModel]:
        stmt = select(TranscriptModel).where(TranscriptModel.resource_id == resource_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, resource_id: UUID, language: str, source_type: str, full_text: str = None) -> TranscriptModel:
        t = TranscriptModel(
            resource_id=resource_id,
            language=language,
            source_type=source_type,
            full_text=full_text,
            status="AVAILABLE"
        )
        self.db.add(t)
        self.db.flush()
        return t

    def update_status(self, transcript_id: UUID, status: str):
        stmt = update(TranscriptModel).where(TranscriptModel.id == transcript_id).values(status=status)
        self.db.execute(stmt)
        self.db.flush()

    def bulk_create_segments(self, segments: List[dict]):
        if not segments:
            return
        stmt = pg_insert(TranscriptSegmentModel).values(segments)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=['transcript_id', 'segment_index']
        )
        self.db.execute(stmt)
        self.db.flush()
