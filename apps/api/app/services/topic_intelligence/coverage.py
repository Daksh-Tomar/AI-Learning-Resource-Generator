from typing import List
from app.schemas.retrieval import RerankedCandidate

class CoverageEstimator:
    def __init__(self, strong_threshold: float = 0.8, moderate_threshold: float = 0.5):
        self.strong_threshold = strong_threshold
        self.moderate_threshold = moderate_threshold

    def estimate_coverage(self, evidence_candidates: List[RerankedCandidate]) -> str:
        """
        Estimates the coverage strength (STRONG, MODERATE, WEAK) based on evidence.
        """
        if not evidence_candidates:
            return "NONE"
            
        # Simplistic heuristic: Max reranker score
        max_score = max([c.scores.reranker_score or 0.0 for c in evidence_candidates])
        
        if max_score >= self.strong_threshold:
            return "STRONG"
        elif max_score >= self.moderate_threshold:
            return "MODERATE"
        else:
            return "WEAK"
