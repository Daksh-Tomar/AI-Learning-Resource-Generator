import asyncio
from uuid import uuid4
import sys
import os

# Add apps/api to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.search_session import SearchSession, SearchPlanModel
from app.models.learner_profile import LearnerProfileModel
from app.services.discovery.service import DiscoveryService
from app.services.ingestion.orchestrator import IngestionOrchestrator
from app.services.providers.youtube.provider import YouTubeProvider
from app.services.providers.youtube.transcript import YouTubeTranscriptProvider
from app.core.config import settings

async def main():
    if not settings.YOUTUBE_API_KEY:
        print("YOUTUBE_API_KEY not configured. Cannot verify.")
        return
        
    db = SessionLocal()
    try:
        # Create a mock session and plan
        session_id = uuid4()
        profile_id = uuid4()
        convo_id = uuid4()
        
        from app.models.conversation import Conversation
        convo = Conversation(id=convo_id)
        db.add(convo)
        db.flush()
        
        profile = LearnerProfileModel(
            id=profile_id,
            conversation_id=convo_id,
            subject="Python",
            goal="Learn python basics",
            current_level="Beginner",
            target_level="Intermediate",
            deadline_days=30,
            daily_hours=2.0
        )
        db.add(profile)
        session = SearchSession(id=session_id, learner_profile_id=profile_id, status="PLANNING")
        db.add(session)
        
        plan = SearchPlanModel(
            search_session_id=session_id,
            primary_topic="Python",
            search_queries=["Introduction to python", "Python tutorials for beginners"],
            project_queries=["Python project ideas for beginners"],
            interview_queries=[]
        )
        db.add(plan)
        db.commit()
        
        print(f"Created Session: {session_id}")
        
        provider = YouTubeProvider(api_key=settings.YOUTUBE_API_KEY)
        transcript_provider = YouTubeTranscriptProvider()
        
        # 1. Discovery
        discovery_svc = DiscoveryService(db, provider, max_results_per_query=3, max_ingestion_candidates=2)
        summary = await discovery_svc.execute_discovery(session_id, plan)
        print("Discovery Summary:")
        print(summary.model_dump_json(indent=2))
        
        # 2. Ingestion
        orchestrator = IngestionOrchestrator(db, provider, transcript_provider, provider)
        ingestion_summary = await orchestrator.ingest_search_session(session_id)
        print("Ingestion Summary:")
        print(ingestion_summary.model_dump_json(indent=2))
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
