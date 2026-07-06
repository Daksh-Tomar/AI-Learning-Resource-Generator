from sqlalchemy.orm import Session
from uuid import UUID
import logging
from typing import Dict, Any

from app.models.search_session import SearchSession
from app.models.discovery_result import DiscoveryResultModel
from app.models.resource import ResourceModel
from app.repositories.ingestion_jobs import IngestionJobRepository
from app.schemas.ingestion import IngestionSummary, IngestionProgress
from app.services.providers.interfaces import ResourceProvider, TranscriptProvider, CommentProvider
from app.services.ingestion.metadata import MetadataIngestionService
from app.services.ingestion.metrics import MetricsIngestionService
from app.services.ingestion.transcripts import TranscriptIngestionService
from app.services.ingestion.comments import CommentIngestionService
from sqlalchemy import select

logger = logging.getLogger(__name__)

class IngestionOrchestrator:
    def __init__(self, 
                 db: Session, 
                 resource_provider: ResourceProvider,
                 transcript_provider: TranscriptProvider,
                 comment_provider: CommentProvider):
        self.db = db
        self.job_repo = IngestionJobRepository(db)
        
        self.metadata_service = MetadataIngestionService(db, resource_provider)
        self.metrics_service = MetricsIngestionService(db, resource_provider)
        self.transcript_service = TranscriptIngestionService(db, transcript_provider)
        self.comment_service = CommentIngestionService(db, comment_provider)
        
    async def ingest_search_session(self, session_id: UUID) -> IngestionSummary:
        logger.info(f"Starting synchronous ingestion for session {session_id}")
        
        # 1. Update session state to INGESTING
        session = self.db.execute(select(SearchSession).where(SearchSession.id == session_id)).scalar_one_or_none()
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.status = "INGESTING"
        self.db.commit()
        
        # 2. Get candidates selected for ingestion
        stmt = (
            select(ResourceModel)
            .join(DiscoveryResultModel, DiscoveryResultModel.resource_id == ResourceModel.id)
            .where(
                DiscoveryResultModel.search_session_id == session_id,
                DiscoveryResultModel.selected_for_ingestion == True
            )
            .distinct()
        )
        resources = self.db.execute(stmt).scalars().all()
        
        if not resources:
            session.status = "INGESTION_COMPLETE"
            self.db.commit()
            return self._build_summary(session_id, "INGESTION_COMPLETE", 0)

        # 3. Create or ensure jobs exist
        for r in resources:
            for job_type in ["METADATA", "METRICS", "TRANSCRIPT", "COMMENTS"]:
                # simple upsert/create if not exists
                # For Phase 1 we will just create them, in a real app we'd check for existing
                self.job_repo.create_job(session_id, r.id, job_type)
        self.db.commit()
        
        # 4. Fetch Metadata
        self._mark_jobs_running(session_id, "METADATA")
        meta_results = await self.metadata_service.fetch_metadata_batch(resources)
        
        # Apply metadata to resources
        for r in resources:
            res = meta_results.get(r.id, {})
            if res.get("status") == "SUCCESS":
                r.title = res.get("title", r.title)
                r.description = res.get("description", r.description)
                r.creator_name = res.get("creator_name", r.creator_name)
                r.published_at = res.get("published_at", r.published_at)
                r.duration_seconds = res.get("duration_seconds", r.duration_seconds)
                r.language = res.get("language", r.language)
        self.db.commit()
        self._update_jobs(session_id, "METADATA", meta_results)
        
        # 5. Fetch Metrics
        self._mark_jobs_running(session_id, "METRICS")
        metric_results = await self.metrics_service.fetch_metrics_batch(resources)
        self._update_jobs(session_id, "METRICS", metric_results)
        
        # 6. Fetch Transcripts
        self._mark_jobs_running(session_id, "TRANSCRIPT")
        transcript_results = await self.transcript_service.fetch_transcripts_batch(resources)
        self._update_jobs(session_id, "TRANSCRIPT", transcript_results)
        
        # 7. Fetch Comments
        self._mark_jobs_running(session_id, "COMMENTS")
        comment_results = await self.comment_service.fetch_comments_batch(resources)
        self._update_jobs(session_id, "COMMENTS", comment_results)
        
        # 8. Mark Session Complete
        session.status = "INGESTION_COMPLETE"
        self.db.commit()
        
        return self._build_summary(session_id, "INGESTION_COMPLETE", len(resources))

    def _mark_jobs_running(self, session_id: UUID, job_type: str):
        from sqlalchemy import update
        from app.models.ingestion_job import IngestionJobModel
        stmt = (
            update(IngestionJobModel)
            .where(
                IngestionJobModel.search_session_id == session_id,
                IngestionJobModel.job_type == job_type,
                IngestionJobModel.status.in_(["PENDING", "FAILED"])
            )
            .values(status="RUNNING")
        )
        self.db.execute(stmt)
        self.db.commit()

    def _update_jobs(self, session_id: UUID, job_type: str, results: Dict[UUID, Dict[str, Any]]):
        from sqlalchemy import select
        from app.models.ingestion_job import IngestionJobModel
        
        stmt = select(IngestionJobModel).where(
            IngestionJobModel.search_session_id == session_id,
            IngestionJobModel.job_type == job_type
        )
        jobs = self.db.execute(stmt).scalars().all()
        
        for job in jobs:
            res = results.get(job.resource_id)
            if res:
                self.job_repo.update_job_status(job.id, res["status"], error_message=res.get("error_message"))
            else:
                self.job_repo.update_job_status(job.id, "SKIPPED", error_message="No result returned")
        self.db.commit()

    def _build_summary(self, session_id: UUID, status: str, total_resources: int) -> IngestionSummary:
        progress = self.job_repo.get_session_progress(session_id)
        
        def to_prog(data):
            return IngestionProgress(
                completed=data.get("completed", 0),
                failed=data.get("failed", 0),
                skipped=data.get("skipped", 0)
            )
            
        return IngestionSummary(
            search_session_id=session_id,
            status=status,
            total_resources=total_resources,
            metadata=to_prog(progress.get("METADATA", {})),
            transcripts=to_prog(progress.get("TRANSCRIPT", {})),
            comments=to_prog(progress.get("COMMENTS", {})),
            metrics=to_prog(progress.get("METRICS", {}))
        )
