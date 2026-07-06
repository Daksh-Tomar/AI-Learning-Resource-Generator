from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID
import logging

from app.models.resource import ResourceModel
from app.repositories.comment import CommentRepository
from app.services.providers.interfaces import CommentProvider
from app.services.providers.youtube.exceptions import CommentsDisabledError

logger = logging.getLogger(__name__)

class CommentIngestionService:
    def __init__(self, db: Session, provider: CommentProvider, max_comments: int = 100):
        self.db = db
        self.provider = provider
        self.comment_repo = CommentRepository(db)
        self.max_comments = max_comments

    async def fetch_comments_batch(self, resources: List[ResourceModel]) -> Dict[UUID, Dict[str, Any]]:
        result = {}
        for r in resources:
            logger.info(f"Fetching comments for {r.external_id}")
            try:
                batch = self.comment_repo.create_batch(
                    resource_id=r.id,
                    provider="YOUTUBE",
                    limit=self.max_comments,
                    order_mode="relevance"
                )
                
                comments_dto = await self.provider.fetch_comments(r.external_id, limit=self.max_comments, order_mode="relevance")
                
                comments_data = []
                for c in comments_dto:
                    # Basic validation: reject empty
                    if not c.text or not c.text.strip():
                        continue
                    comments_data.append({
                        "resource_id": r.id,
                        "collection_batch_id": batch.id,
                        "external_comment_id": c.external_comment_id,
                        "text": c.text,
                        "like_count": max(0, c.like_count) if c.like_count else 0,
                        "published_at": c.published_at
                    })
                    
                if comments_data:
                    self.comment_repo.bulk_upsert(comments_data)
                
                self.comment_repo.update_batch_count(batch.id, len(comments_data))
                self.db.commit()
                
                result[r.id] = {"status": "SUCCESS"}
            except CommentsDisabledError as e:
                logger.warning(f"Comments disabled for {r.external_id}")
                self.db.commit() # save batch with 0 count
                result[r.id] = {"status": "SKIPPED", "error_message": str(e)}
            except Exception as e:
                logger.error(f"Failed to fetch comments for {r.external_id}: {e}")
                self.db.rollback()
                result[r.id] = {"status": "FAILED", "error_message": str(e)}
                
        return result
