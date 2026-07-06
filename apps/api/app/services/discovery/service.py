from typing import List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
import logging

from app.models.search_session import SearchSession, SearchPlanModel
from app.schemas.ingestion import ResourceCandidate
from app.schemas.discovery import DiscoverySummary
from app.services.providers.interfaces import ResourceProvider
from app.repositories.search_queries import SearchQueryRepository
from app.repositories.discovery_results import DiscoveryResultRepository
from app.repositories.resource import ResourceRepository
from .deduplication import DeduplicationService
from .candidate_selection import CandidateSelectionService

logger = logging.getLogger(__name__)

class DiscoveryService:
    def __init__(self, 
                 db: Session, 
                 provider: ResourceProvider, 
                 max_queries: int = 8, 
                 max_results_per_query: int = 20,
                 max_ingestion_candidates: int = 40):
        self.db = db
        self.provider = provider
        self.max_queries = max_queries
        self.max_results_per_query = max_results_per_query
        self.max_ingestion_candidates = max_ingestion_candidates
        
        self.search_query_repo = SearchQueryRepository(db)
        self.discovery_result_repo = DiscoveryResultRepository(db)
        self.resource_repo = ResourceRepository(db)
        self.dedup_service = DeduplicationService()
        self.candidate_service = CandidateSelectionService()

    async def execute_discovery(self, search_session_id: UUID, search_plan: SearchPlanModel) -> DiscoverySummary:
        logger.info(f"Starting discovery for session {search_session_id}")
        
        # 1. Build queries from plan
        queries_to_run = []
        for q in search_plan.search_queries:
            queries_to_run.append((q, "GENERAL"))
        for q in search_plan.project_queries:
            queries_to_run.append((q, "PROJECT"))
        for q in search_plan.interview_queries:
            queries_to_run.append((q, "INTERVIEW"))
            
        queries_to_run = queries_to_run[:self.max_queries]
        
        raw_candidates: List[Tuple[ResourceCandidate, dict]] = []
        queries_executed = 0
        
        # 2. Execute queries
        for query_text, query_type in queries_to_run:
            query_model = self.search_query_repo.create(
                search_session_id=search_session_id,
                query_text=query_text,
                query_type=query_type,
                provider=self.provider.provider_name
            )
            
            try:
                results = await self.provider.search(query=query_text, limit=self.max_results_per_query)
                queries_executed += 1
                
                self.search_query_repo.update_status(query_model.id, "SUCCESS", result_count=len(results))
                
                for rank, candidate in enumerate(results, start=1):
                    raw_candidates.append((candidate, {
                        "query_id": query_model.id,
                        "query_type": query_type,
                        "rank": rank
                    }))
                    
            except Exception as e:
                logger.error(f"Query '{query_text}' failed: {e}")
                self.search_query_repo.update_status(query_model.id, "FAILED", error_message=str(e))
                # Continue with other queries
                
        # 3. Deduplicate
        unique_groups = self.dedup_service.deduplicate_candidates(raw_candidates)
        
        # 4. Upsert resources
        resources_to_insert = []
        for candidate, _ in unique_groups:
            resources_to_insert.append({
                "external_id": candidate.external_id,
                "provider": self.provider.provider_name,
                "resource_type": "VIDEO",
                "title": candidate.title,
                "url": candidate.url,
                "description": candidate.description,
                "creator_name": candidate.creator_name,
                "published_at": candidate.published_at,
                "duration_seconds": candidate.duration_seconds
            })
            
        upserted_resources = self.resource_repo.bulk_upsert(resources_to_insert)
        
        # Map external_id back to resource_id
        ext_to_resource_id = {r.external_id: r.id for r in upserted_resources}
        
        # 5. Save discovery results
        discovery_rows = []
        for candidate, query_infos in unique_groups:
            resource_id = ext_to_resource_id.get(candidate.external_id)
            if not resource_id:
                continue
            for q_info in query_infos:
                discovery_rows.append({
                    "search_session_id": search_session_id,
                    "search_query_id": q_info["query_id"],
                    "resource_id": resource_id,
                    "provider_rank": q_info["rank"]
                })
                
        self.discovery_result_repo.bulk_create(discovery_rows)
        
        # 6. Candidate Selection (Calculate priority score and select)
        query_freqs = self.discovery_result_repo.get_query_frequency_for_session(search_session_id)
        query_divs = self.discovery_result_repo.get_query_diversity_for_session(search_session_id)
        
        scores: Dict[UUID, float] = {}
        for candidate, query_infos in unique_groups:
            resource_id = ext_to_resource_id.get(candidate.external_id)
            if not resource_id:
                continue
                
            best_rank = min((q["rank"] for q in query_infos), default=50)
            freq = query_freqs.get(resource_id, 1)
            div = query_divs.get(resource_id, 1)
            
            score = self.candidate_service.calculate_priority_score(
                best_rank=best_rank,
                query_freq=freq,
                query_diversity=div,
                has_title=bool(candidate.title),
                has_duration=bool(candidate.duration_seconds)
            )
            scores[resource_id] = score
            
        selected_ids = self.candidate_service.select_top_candidates(scores, self.max_ingestion_candidates)
        
        # Update selection and scores in DB
        self.discovery_result_repo.update_ingestion_selection(search_session_id, selected_ids, scores)
        self.db.commit() # Commit transaction
        
        return DiscoverySummary(
            search_session_id=search_session_id,
            status="DISCOVERY_COMPLETE",
            queries_executed=queries_executed,
            raw_results=len(raw_candidates),
            unique_candidates=len(unique_groups),
            selected_for_ingestion=len(selected_ids)
        )
