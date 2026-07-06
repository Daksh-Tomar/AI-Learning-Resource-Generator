from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID

from app.models.resource import ResourceModel
from app.repositories.resource import ResourceRepository
from app.services.providers.interfaces import ResourceProvider
import logging

logger = logging.getLogger(__name__)

class MetadataIngestionService:
    def __init__(self, db: Session, provider: ResourceProvider):
        self.db = db
        self.provider = provider
        self.resource_repo = ResourceRepository(db)

    async def fetch_metadata_batch(self, resources: List[ResourceModel]) -> Dict[UUID, Dict[str, Any]]:
        if not resources:
            return {}
            
        external_ids = [r.external_id for r in resources]
        logger.info(f"Fetching metadata for {len(external_ids)} resources via {self.provider.provider_name}")
        
        try:
            metadata_list = await self.provider.fetch_metadata(external_ids)
            
            # Map back to internal format
            result = {}
            for r in resources:
                meta = next((m for m in metadata_list if m.external_id == r.external_id), None)
                if meta:
                    result[r.id] = {
                        "status": "SUCCESS",
                        "title": meta.title,
                        "description": meta.description,
                        "creator_name": meta.creator_name,
                        "published_at": meta.published_at,
                        "duration_seconds": meta.duration_seconds,
                        "language": meta.language
                    }
                else:
                    result[r.id] = {
                        "status": "UNAVAILABLE",
                        "error_message": "Metadata not returned by provider"
                    }
            return result
        except Exception as e:
            logger.error(f"Metadata fetch failed: {e}")
            return {r.id: {"status": "FAILED", "error_message": str(e)} for r in resources}
