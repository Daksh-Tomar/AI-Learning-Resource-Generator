from typing import List, Dict
from uuid import UUID
from app.schemas.retrieval import RetrievalCandidate

class ReciprocalRankFusion:
    def __init__(self, k: int = 60):
        # k is the RRF constant (default 60 is standard)
        self.k = k

    def fuse(
        self, 
        dense_results: List[RetrievalCandidate], 
        lexical_results: List[RetrievalCandidate],
        top_k: int = 20
    ) -> List[RetrievalCandidate]:
        
        candidates_map: Dict[UUID, RetrievalCandidate] = {}
        
        # Process dense results
        for rank, candidate in enumerate(dense_results, start=1):
            if candidate.chunk_id not in candidates_map:
                candidates_map[candidate.chunk_id] = candidate
                # initialize score components if they are unset
            
            candidates_map[candidate.chunk_id].ranks.dense_rank = rank
            candidates_map[candidate.chunk_id].scores.dense_similarity = candidate.scores.dense_similarity
            
        # Process lexical results
        for rank, candidate in enumerate(lexical_results, start=1):
            if candidate.chunk_id not in candidates_map:
                candidates_map[candidate.chunk_id] = candidate
                
            candidates_map[candidate.chunk_id].ranks.lexical_rank = rank
            candidates_map[candidate.chunk_id].scores.lexical_score = candidate.scores.lexical_score
            
        # Calculate RRF Score
        for chunk_id, candidate in candidates_map.items():
            rrf_score = 0.0
            
            if candidate.ranks.dense_rank is not None:
                rrf_score += 1.0 / (self.k + candidate.ranks.dense_rank)
                
            if candidate.ranks.lexical_rank is not None:
                rrf_score += 1.0 / (self.k + candidate.ranks.lexical_rank)
                
            candidate.scores.rrf_score = rrf_score
            
        # Sort by RRF score descending
        fused_candidates = list(candidates_map.values())
        fused_candidates.sort(key=lambda x: x.scores.rrf_score or 0.0, reverse=True)
        
        # Assign fusion ranks
        for rank, candidate in enumerate(fused_candidates, start=1):
            candidate.ranks.fusion_rank = rank
            
        return fused_candidates[:top_k]
