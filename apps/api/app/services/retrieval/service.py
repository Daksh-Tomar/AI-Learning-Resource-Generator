from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from uuid import UUID
from app.schemas.retrieval import RetrievalCandidate, RerankedCandidate
from .dense import DenseRetriever
from .lexical import LexicalRetriever
from .fusion import ReciprocalRankFusion
from .reranker import CrossEncoderReranker

class RetrievalService:
    def __init__(self, db: Session):
        self.db = db
        self.dense_retriever = DenseRetriever(db)
        self.lexical_retriever = LexicalRetriever(db)
        self.fusion = ReciprocalRankFusion()
        # Initialize lazily or pass in dependency for reranker
        self.reranker = CrossEncoderReranker()

    async def search(
        self,
        query: str,
        resource_id_filter: Optional[str] = None,
        top_k: int = 20,
        use_reranker: bool = True
    ) -> List[RerankedCandidate]:
        
        # 1. Dense Retrieval
        dense_results = await self.dense_retriever.retrieve(
            query=query, 
            top_k=top_k * 2, # Fetch more for fusion/reranking
            resource_id_filter=resource_id_filter
        )
        
        # 2. Lexical Retrieval
        lexical_results = self.lexical_retriever.retrieve(
            query=query, 
            top_k=top_k * 2,
            resource_id_filter=resource_id_filter
        )
        
        # 3. Fusion
        fused_candidates = self.fusion.fuse(dense_results, lexical_results, top_k=top_k*2 if use_reranker else top_k)
        
        # 4. Reranking
        if use_reranker:
            final_candidates = await self.reranker.rerank(query, fused_candidates, top_k=top_k)
            return final_candidates
            
        return [RerankedCandidate(**c.model_dump()) for c in fused_candidates]

    def aggregate_resource_relevance(self, candidates: List[RerankedCandidate]) -> Dict[UUID, float]:
        """
        Aggregate chunk-level retrieval scores into resource-level relevance scores.
        Simple heuristic: sum of top-K chunk scores for the resource.
        """
        resource_scores = {}
        for c in candidates:
            score = c.scores.reranker_score or c.scores.rrf_score or 0.0
            if c.resource_id not in resource_scores:
                resource_scores[c.resource_id] = 0.0
            resource_scores[c.resource_id] += score
            
        return resource_scores
