from sqlalchemy.orm import Session
from typing import List, Dict, Any
from uuid import UUID
import logging
from datetime import datetime, timezone

from app.models.resource import ResourceModel
from app.repositories.resource_metrics import ResourceMetricsRepository
from app.services.providers.interfaces import ResourceProvider

logger = logging.getLogger(__name__)

class MetricsIngestionService:
    def __init__(self, db: Session, provider: ResourceProvider):
        self.db = db
        self.provider = provider
        self.metrics_repo = ResourceMetricsRepository(db)

    async def fetch_metrics_batch(self, resources: List[ResourceModel]) -> Dict[UUID, Dict[str, Any]]:
        if not resources:
            return {}
            
        external_ids = [r.external_id for r in resources]
        logger.info(f"Fetching metrics for {len(external_ids)} resources via {self.provider.provider_name}")
        
        try:
            engagement_list = await self.provider.fetch_engagement_data(external_ids)
            
            # Persist raw snapshots
            snapshots_to_create = []
            result = {}
            for r in resources:
                eng = next((e for e in engagement_list if e.external_id == r.external_id), None)
                if eng:
                    snapshots_to_create.append({
                        "resource_id": r.id,
                        "view_count": eng.view_count,
                        "like_count": eng.like_count,
                        "comment_count": eng.comment_count
                    })
                    result[r.id] = {"status": "SUCCESS"}
                else:
                    result[r.id] = {"status": "UNAVAILABLE", "error_message": "Metrics not returned"}
            
            if snapshots_to_create:
                self.metrics_repo.bulk_create_snapshots(snapshots_to_create)
                self.db.commit()
                
            return result
        except Exception as e:
            logger.error(f"Metrics fetch failed: {e}")
            self.db.rollback()
            return {r.id: {"status": "FAILED", "error_message": str(e)} for r in resources}

    def calculate_derived_metrics(self, resource: ResourceModel) -> Dict[str, float]:
        """Calculates simple deterministic metrics on the fly."""
        latest = self.metrics_repo.get_latest_snapshot(resource.id)
        if not latest:
            return {}
            
        metrics = {}
        vc = latest.view_count or 0
        lc = latest.like_count
        cc = latest.comment_count
        
        safe_vc = max(vc, 1)
        
        if lc is not None:
            metrics["like_view_ratio"] = lc / safe_vc
        if cc is not None:
            metrics["comment_view_ratio"] = cc / safe_vc
            
        if lc is not None and cc is not None:
            metrics["basic_engagement_rate"] = (lc + cc) / safe_vc
            
        if resource.published_at:
            age_days = (datetime.now(timezone.utc) - resource.published_at).days
            safe_age = max(age_days, 1)
            metrics["views_per_day"] = vc / safe_age
            metrics["video_age_days"] = age_days
            
        return metrics
