from typing import List, Optional
from sqlalchemy.orm import Session
from app.services.retrieval.service import RetrievalService
from app.schemas.retrieval import RerankedCandidate

class ConceptEvidenceRetriever:
    def __init__(self, db: Session):
        self.db = db
        self.retrieval_service = RetrievalService(db)

    async def retrieve_evidence(self, concept_query: str, resource_id: str, top_k: int = 5) -> List[RerankedCandidate]:
        """
        Retrieves top evidence chunks for a specific concept within a specific resource.
        """
        candidates = await self.retrieval_service.search(
            query=concept_query,
            resource_id_filter=resource_id,
            top_k=top_k,
            use_reranker=True
        )
        return candidates
