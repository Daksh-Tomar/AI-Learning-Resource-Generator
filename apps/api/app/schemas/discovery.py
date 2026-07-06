from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class DiscoverySummary(BaseModel):
    search_session_id: UUID
    status: str
    queries_executed: int
    raw_results: int
    unique_candidates: int
    selected_for_ingestion: int
