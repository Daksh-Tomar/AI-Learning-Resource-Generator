from sqlalchemy.orm import Session
from sqlalchemy import select, update
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.models.ingestion_job import IngestionJobModel

class IngestionJobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, session_id: UUID, resource_id: UUID, job_type: str) -> IngestionJobModel:
        job = IngestionJobModel(
            search_session_id=session_id,
            resource_id=resource_id,
            job_type=job_type,
            status="PENDING"
        )
        self.db.add(job)
        self.db.flush()
        return job

    def bulk_create_jobs(self, jobs: List[dict]) -> List[IngestionJobModel]:
        if not jobs:
            return []
        objs = [IngestionJobModel(**j) for j in jobs]
        self.db.add_all(objs)
        self.db.flush()
        return objs

    def get_session_progress(self, session_id: UUID) -> Dict[str, Any]:
        stmt = select(IngestionJobModel).where(IngestionJobModel.search_session_id == session_id)
        result = self.db.execute(stmt).scalars().all()
        
        progress = {
            "METADATA": {"completed": 0, "failed": 0, "skipped": 0},
            "TRANSCRIPT": {"completed": 0, "failed": 0, "skipped": 0},
            "COMMENTS": {"completed": 0, "failed": 0, "skipped": 0},
            "METRICS": {"completed": 0, "failed": 0, "skipped": 0},
        }
        
        for job in result:
            if job.job_type in progress:
                if job.status == "SUCCESS":
                    progress[job.job_type]["completed"] += 1
                elif job.status == "FAILED":
                    progress[job.job_type]["failed"] += 1
                elif job.status in ("SKIPPED", "UNAVAILABLE"):
                    progress[job.job_type]["skipped"] += 1
                    
        return progress

    def update_job_status(self, job_id: UUID, status: str, error_code: str = None, error_message: str = None) -> IngestionJobModel:
        from datetime import datetime
        update_data = {
            "status": status,
            "last_attempt_at": datetime.utcnow()
        }
        if status == "RUNNING":
            # Avoid overwriting started_at on retries if we don't want to
            update_data["started_at"] = datetime.utcnow()
            update_data["attempt_count"] = IngestionJobModel.attempt_count + 1
        elif status in ("SUCCESS", "FAILED", "SKIPPED"):
            update_data["completed_at"] = datetime.utcnow()
            
        if error_code:
            update_data["error_code"] = error_code
        if error_message:
            update_data["error_message"] = error_message
            
        stmt = (
            update(IngestionJobModel)
            .where(IngestionJobModel.id == job_id)
            .values(**update_data)
            .returning(IngestionJobModel)
        )
        job = self.db.execute(stmt).scalar_one_or_none()
        self.db.flush()
        return job
