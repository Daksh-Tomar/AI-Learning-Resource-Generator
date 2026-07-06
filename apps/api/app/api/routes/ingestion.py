from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Any

from app.core.database import get_db
from app.schemas.ingestion import IngestionSummary
from app.services.ingestion.orchestrator import IngestionOrchestrator
from app.services.providers.youtube.provider import YouTubeProvider
from app.services.providers.youtube.transcript import YouTubeTranscriptProvider
from app.core.config import settings

router = APIRouter()

def get_orchestrator(db: Session = Depends(get_db)):
    if not settings.YOUTUBE_API_KEY:
        raise HTTPException(status_code=500, detail="YouTube API Key not configured")
    provider = YouTubeProvider(api_key=settings.YOUTUBE_API_KEY)
    transcript_provider = YouTubeTranscriptProvider()
    return IngestionOrchestrator(db, provider, transcript_provider, provider)

@router.post("/{session_id}/ingest", response_model=IngestionSummary)
async def start_ingestion(
    session_id: UUID, 
    orchestrator: IngestionOrchestrator = Depends(get_orchestrator)
):
    summary = await orchestrator.ingest_search_session(session_id)
    return summary

@router.get("/{session_id}/status", response_model=IngestionSummary)
async def get_ingestion_status(session_id: UUID, db: Session = Depends(get_db), orchestrator: IngestionOrchestrator = Depends(get_orchestrator)):
    from app.models.search_session import SearchSession
    from sqlalchemy import select
    
    session = db.execute(select(SearchSession).where(SearchSession.id == session_id)).scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Search session not found")
        
    return orchestrator._build_summary(session_id, session.status, 0)
