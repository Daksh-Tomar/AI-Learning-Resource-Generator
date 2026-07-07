from typing import List
import math

class RetrievalMetrics:
    @staticmethod
    def recall_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
        """Calculate Recall@K."""
        if not relevant_ids:
            return 0.0
        retrieved_k = retrieved_ids[:k]
        hits = sum(1 for rid in relevant_ids if rid in retrieved_k)
        return hits / len(relevant_ids)

    @staticmethod
    def mrr(retrieved_ids: List[str], relevant_ids: List[str]) -> float:
        """Calculate Mean Reciprocal Rank."""
        for i, rid in enumerate(retrieved_ids):
            if rid in relevant_ids:
                return 1.0 / (i + 1)
        return 0.0

    @staticmethod
    def ndcg_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
        """Calculate Normalized Discounted Cumulative Gain at K."""
        def dcg(retrieved, relevant):
            score = 0.0
            for i, rid in enumerate(retrieved):
                if rid in relevant:
                    score += 1.0 / math.log2(i + 2)
            return score
            
        retrieved_k = retrieved_ids[:k]
        actual_dcg = dcg(retrieved_k, relevant_ids)
        ideal_dcg = dcg(relevant_ids[:k], relevant_ids)
        
        if ideal_dcg == 0.0:
            return 0.0
        return actual_dcg / ideal_dcg
