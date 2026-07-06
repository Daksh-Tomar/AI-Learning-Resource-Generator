from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.comment import CommentModel, CommentCollectionBatchModel

class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_batch(self, resource_id: UUID, provider: str, limit: int, order_mode: str, actual_count: int = 0) -> CommentCollectionBatchModel:
        batch = CommentCollectionBatchModel(
            resource_id=resource_id,
            provider=provider,
            requested_limit=limit,
            order_mode=order_mode,
            actual_count=actual_count
        )
        self.db.add(batch)
        self.db.flush()
        return batch

    def update_batch_count(self, batch_id: UUID, count: int):
        from sqlalchemy import update
        stmt = update(CommentCollectionBatchModel).where(CommentCollectionBatchModel.id == batch_id).values(actual_count=count)
        self.db.execute(stmt)
        self.db.flush()

    def bulk_upsert(self, comments: List[dict]):
        if not comments:
            return
        stmt = pg_insert(CommentModel).values(comments)
        
        update_dict = {
            c.name: c for c in stmt.excluded 
            if c.name in ["text", "like_count", "published_at"]
        }
        
        # We can conflict on external_comment_id if we want unique comments globally
        # But we don't have unique constraint. Let's create one or just use plain insert.
        # Phase 1 says "avoid duplicate external comment IDs".
        pass
        
        # We should add a unique constraint in the migration.
        stmt = stmt.on_conflict_do_update(
            index_elements=['external_comment_id'],
            set_=update_dict
        )
        self.db.execute(stmt)
        self.db.flush()
