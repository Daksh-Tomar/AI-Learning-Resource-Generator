from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from typing import List, Optional
from uuid import UUID

from app.models.resource_metrics import ResourceMetrics

class ResourceMetricsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_snapshot(self, resource_id: UUID, view_count: Optional[int], like_count: Optional[int], comment_count: Optional[int]) -> ResourceMetrics:
        snapshot = ResourceMetrics(
            resource_id=resource_id,
            view_count=view_count or 0,
            like_count=like_count,
            comment_count=comment_count
        )
        self.db.add(snapshot)
        self.db.flush()
        return snapshot

    def bulk_create_snapshots(self, snapshots: List[dict]) -> List[ResourceMetrics]:
        if not snapshots:
            return []
        
        objs = [ResourceMetrics(**s) for s in snapshots]
        self.db.add_all(objs)
        self.db.flush()
        return objs

    def get_latest_snapshot(self, resource_id: UUID) -> Optional[ResourceMetrics]:
        stmt = (
            select(ResourceMetrics)
            .where(ResourceMetrics.resource_id == resource_id)
            .order_by(desc(ResourceMetrics.collected_at))
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()
