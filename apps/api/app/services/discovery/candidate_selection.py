from typing import List, Dict
from uuid import UUID

class CandidateSelectionService:
    def __init__(self, weights: Dict[str, float] = None):
        # Default weights for Phase 1 heuristic
        self.weights = weights or {
            "rank": 0.45,
            "frequency": 0.30,
            "diversity": 0.15,
            "metadata_validity": 0.10
        }

    def calculate_priority_score(self, 
                                 best_rank: int, 
                                 query_freq: int, 
                                 query_diversity: int, 
                                 has_title: bool, 
                                 has_duration: bool) -> float:
        # Normalize rank: 1 is best, assume 50 is max
        rank_score = max(0.0, 1.0 - (best_rank - 1) / 50.0)
        
        # Normalize freq (assume max freq is roughly 10)
        freq_score = min(1.0, query_freq / 5.0)
        
        # Normalize diversity (assume max is 4 categories)
        div_score = min(1.0, query_diversity / 3.0)
        
        # Basic validity
        validity_score = 0.0
        if has_title:
            validity_score += 0.5
        if has_duration:
            validity_score += 0.5
            
        score = (
            self.weights["rank"] * rank_score +
            self.weights["frequency"] * freq_score +
            self.weights["diversity"] * div_score +
            self.weights["metadata_validity"] * validity_score
        )
        return score

    def select_top_candidates(self, candidates_scores: Dict[UUID, float], max_candidates: int) -> List[UUID]:
        # Sort by score descending
        sorted_candidates = sorted(candidates_scores.items(), key=lambda x: x[1], reverse=True)
        return [c[0] for c in sorted_candidates[:max_candidates]]
