from typing import List, Dict, Tuple
from app.schemas.ingestion import ResourceCandidate
from app.models.resource import ResourceModel

class DeduplicationService:
    @staticmethod
    def deduplicate_candidates(candidates: List[Tuple[ResourceCandidate, dict]]) -> List[Tuple[ResourceCandidate, List[dict]]]:
        """
        Takes a list of (candidate, query_info) and deduplicates based on external_id.
        Returns a list of unique candidates, each paired with all the query_infos that found it.
        """
        unique_map: Dict[str, Tuple[ResourceCandidate, List[dict]]] = {}
        
        for candidate, query_info in candidates:
            # We assume all candidates here are from the same provider (e.g. YOUTUBE)
            # If multi-provider in same batch, use f"{provider}_{candidate.external_id}"
            key = candidate.external_id
            if key not in unique_map:
                unique_map[key] = (candidate, [query_info])
            else:
                unique_map[key][1].append(query_info)
                
        return list(unique_map.values())
