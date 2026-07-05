from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.search_plan import SearchPlanRequest, SearchPlanResponse
from app.repositories.profile import profile_repo
from app.schemas.learner_profile import LearnerProfileSchema
from app.services.query_planning.generator import SearchPlanGenerator
import logging

router = APIRouter(prefix="/api/search-plan", tags=["search"])
logger = logging.getLogger("learnlens.api")

@router.post("/generate", response_model=SearchPlanResponse)
def generate_search_plan(request: SearchPlanRequest, db: Session = Depends(get_db)):
    logger.info(f"Generating search plan for profile {request.profile_id}")
    try:
        # Fetch profile
        db_profile = profile_repo.get_by_id(db, request.profile_id)
        if not db_profile:
            raise HTTPException(status_code=404, detail="Profile not found")
            
        # Convert DB model back to schema to pass to generator
        # (Alternatively, create a from_orm on the schema, but since some fields are JSON, we do it manually)
        profile_schema = LearnerProfileSchema(
            subject=db_profile.subject,
            goal=db_profile.goal,
            current_level=db_profile.current_level,
            target_level=db_profile.target_level,
            deadline_days=db_profile.deadline_days,
            daily_hours=db_profile.daily_hours,
            known_topics=db_profile.known_topics or [],
            weak_topics=db_profile.weak_topics or [],
            preferred_formats=db_profile.preferred_formats or [],
            preferred_language=db_profile.preferred_language,
            wants_projects=db_profile.wants_projects,
            wants_interview_prep=db_profile.wants_interview_prep
        )
        
        plan = SearchPlanGenerator.generate_plan(profile_schema)
        
        return SearchPlanResponse(
            profile_id=request.profile_id,
            search_plan=plan
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to generate search plan")
        raise HTTPException(status_code=500, detail=str(e))
