from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from typing import List, Dict, Any
from uuid import UUID
from collections import defaultdict

from app.models.discovery_result import DiscoveryResultModel
from app.models.search_query import SearchQueryModel

class DiscoveryResultRepository:
    def __init__(self, db: Session):
        self.db = db

    def bulk_create(self, results: List[dict]) -> List[DiscoveryResultModel]:
        if not results:
            return []
        # PostgreSQL specific bulk insert using standard insert
        # For idempotency, we might need a conflict handling if we rerun discovery?
        # Since Phase 1 says "do not create duplicate discovery rows for the exact same session/query/resource combination"
        # We can use insert().on_conflict_do_nothing()
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        
        stmt = pg_insert(DiscoveryResultModel).values(results)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=['search_query_id', 'resource_id']
        )
        self.db.execute(stmt)
        # Fetching them back is tricky with DO NOTHING if we want to return full models, 
        # but returning None is fine if we just want them inserted.
        self.db.flush()
        return [] # We won't return models for bulk upserts

    def get_query_frequency_for_session(self, session_id: UUID) -> Dict[UUID, int]:
        """Returns mapping of resource_id -> number of queries it appeared in."""
        stmt = (
            select(
                DiscoveryResultModel.resource_id,
                func.count(DiscoveryResultModel.search_query_id).label("freq")
            )
            .where(DiscoveryResultModel.search_session_id == session_id)
            .group_by(DiscoveryResultModel.resource_id)
        )
        result = self.db.execute(stmt).all()
        return {r.resource_id: r.freq for r in result}

    def get_query_diversity_for_session(self, session_id: UUID) -> Dict[UUID, int]:
        """Returns mapping of resource_id -> number of distinct query types it appeared in."""
        stmt = (
            select(
                DiscoveryResultModel.resource_id,
                func.count(func.distinct(SearchQueryModel.query_type)).label("diversity")
            )
            .join(SearchQueryModel, SearchQueryModel.id == DiscoveryResultModel.search_query_id)
            .where(DiscoveryResultModel.search_session_id == session_id)
            .group_by(DiscoveryResultModel.resource_id)
        )
        result = self.db.execute(stmt).all()
        return {r.resource_id: r.diversity for r in result}

    def update_ingestion_selection(self, session_id: UUID, selected_resource_ids: List[UUID], scores: Dict[UUID, float]):
        from sqlalchemy import update
        
        # Mark all selected
        if selected_resource_ids:
            stmt = (
                update(DiscoveryResultModel)
                .where(and_(
                    DiscoveryResultModel.search_session_id == session_id,
                    DiscoveryResultModel.resource_id.in_(selected_resource_ids)
                ))
                .values(selected_for_ingestion=True)
            )
            self.db.execute(stmt)

        # Update scores individually if possible, or batched
        for resource_id, score in scores.items():
            stmt = (
                update(DiscoveryResultModel)
                .where(and_(
                    DiscoveryResultModel.search_session_id == session_id,
                    DiscoveryResultModel.resource_id == resource_id
                ))
                .values(ingestion_priority_score=score)
            )
            self.db.execute(stmt)
        
        self.db.flush()
