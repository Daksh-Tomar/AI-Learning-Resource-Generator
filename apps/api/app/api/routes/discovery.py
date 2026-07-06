from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.models.search_session import SearchSession, SearchPlanModel
from app.schemas.discovery import DiscoverySummary
from app.services.discovery.service import DiscoveryService
from app.services.providers.youtube.provider import YouTubeProvider
from app.core.config import settings
from sqlalchemy import select

router = APIRouter()

def get_discovery_service(db: Session = Depends(get_db)):
    if not settings.YOUTUBE_API_KEY:
        raise HTTPException(status_code=500, detail="YouTube API Key not configured")
    provider = YouTubeProvider(api_key=settings.YOUTUBE_API_KEY)
    return DiscoveryService(db, provider)

@router.post("/{session_id}/discover", response_model=DiscoverySummary)
async def start_discovery(
    session_id: UUID, 
    db: Session = Depends(get_db),
    service: DiscoveryService = Depends(get_discovery_service)
):
    session = db.execute(select(SearchSession).where(SearchSession.id == session_id)).scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Search session not found")
        
    plan = db.execute(select(SearchPlanModel).where(SearchPlanModel.search_session_id == session_id)).scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=400, detail="No search plan found for this session")
        
    session.status = "DISCOVERING"
    db.commit()
    
    summary = await service.execute_discovery(session_id, plan)
    
    session.status = "DISCOVERY_COMPLETE"
    db.commit()
    
    return summary

@router.get("/{session_id}/resources")
async def list_discovered_resources(session_id: UUID, db: Session = Depends(get_db)):
    from app.models.discovery_result import DiscoveryResultModel
    from app.models.resource import ResourceModel
    
    stmt = (
        select(ResourceModel, DiscoveryResultModel.selected_for_ingestion, DiscoveryResultModel.ingestion_priority_score)
        .join(DiscoveryResultModel, DiscoveryResultModel.resource_id == ResourceModel.id)
        .where(DiscoveryResultModel.search_session_id == session_id)
        .distinct()
    )
    results = db.execute(stmt).all()
    
    return [
        {
            "id": r.ResourceModel.id,
            "title": r.ResourceModel.title,
            "url": r.ResourceModel.url,
            "selected_for_ingestion": r.selected_for_ingestion,
            "priority_score": r.ingestion_priority_score
        } for r in results
    ]
