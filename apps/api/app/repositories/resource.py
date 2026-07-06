from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.resource import ResourceModel

class ResourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def bulk_upsert(self, resources: List[dict]) -> List[ResourceModel]:
        """
        Idempotent bulk upsert of resources based on (provider, external_id).
        Returns the list of upserted/existing ResourceModels.
        """
        if not resources:
            return []
            
        stmt = pg_insert(ResourceModel).values(resources)
        
        # On conflict, do update
        update_dict = {
            c.name: c for c in stmt.excluded 
            if not c.primary_key and c.name not in ["id", "created_at"]
        }
        
        stmt = stmt.on_conflict_do_update(
            index_elements=['provider', 'external_id'],
            set_=update_dict
        ).returning(ResourceModel)
        
        result = self.db.execute(stmt)
        self.db.flush()
        return list(result.scalars().all())

    def get_by_provider_external_id(self, provider: str, external_id: str) -> Optional[ResourceModel]:
        stmt = select(ResourceModel).where(
            ResourceModel.provider == provider,
            ResourceModel.external_id == external_id
        )
        return self.db.execute(stmt).scalar_one_or_none()
