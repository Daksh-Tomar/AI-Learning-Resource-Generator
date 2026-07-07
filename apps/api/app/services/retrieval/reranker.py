from typing import Protocol, List
from app.schemas.retrieval import RetrievalCandidate, RerankedCandidate

class Reranker(Protocol):

    async def rerank(
        self,
        query: str,
        candidates: List[RetrievalCandidate],
        top_k: int
    ) -> List[RerankedCandidate]:
        ...


class CrossEncoderReranker(Reranker):
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        import torch
        from sentence_transformers import CrossEncoder
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CrossEncoder(model_name, device=device)

    async def rerank(
        self,
        query: str,
        candidates: List[RetrievalCandidate],
        top_k: int = 20
    ) -> List[RerankedCandidate]:
        if not candidates:
            return []
            
        # Prepare input pairs
        pairs = [[query, candidate.text] for candidate in candidates]
        
        import asyncio
        loop = asyncio.get_running_loop()
        scores = await loop.run_in_executor(
            None,
            lambda p: self.model.predict(p),
            pairs
        )
        
        reranked_candidates = []
        for i, candidate in enumerate(candidates):
            rc = RerankedCandidate(**candidate.model_dump())
            rc.scores.reranker_score = float(scores[i])
            reranked_candidates.append(rc)
            
        # Sort by reranker score
        reranked_candidates.sort(key=lambda x: x.scores.reranker_score or 0.0, reverse=True)
        
        # Assign final ranks
        for rank, candidate in enumerate(reranked_candidates, start=1):
            candidate.ranks.final_rank = rank
            
        return reranked_candidates[:top_k]
