from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.search_query import SearchQueryModel

class SearchQueryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, search_session_id: UUID, query_text: str, query_type: str, provider: str = "YOUTUBE") -> SearchQueryModel:
        query = SearchQueryModel(
            search_session_id=search_session_id,
            query_text=query_text,
            query_type=query_type,
            provider=provider
        )
        self.db.add(query)
        self.db.flush()
        return query

    def bulk_create(self, queries: List[dict]) -> List[SearchQueryModel]:
        if not queries:
            return []
        
        objs = [SearchQueryModel(**q) for q in queries]
        self.db.add_all(objs)
        self.db.flush()
        return objs

    def get_by_session_id(self, session_id: UUID) -> List[SearchQueryModel]:
        stmt = select(SearchQueryModel).where(SearchQueryModel.search_session_id == session_id)
        result = self.db.execute(stmt)
        return list(result.scalars().all())

    def update_status(self, query_id: UUID, status: str, result_count: int = 0, error_code: str = None, error_message: str = None) -> SearchQueryModel:
        stmt = (
            update(SearchQueryModel)
            .where(SearchQueryModel.id == query_id)
            .values(
                execution_status=status,
                result_count=result_count,
                error_code=error_code,
                error_message=error_message,
                executed_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            .returning(SearchQueryModel)
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
