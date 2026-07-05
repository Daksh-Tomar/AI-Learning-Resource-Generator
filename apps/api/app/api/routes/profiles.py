from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.chat import ChatRequest
from app.schemas.learner_profile import LearnerProfileSchema
from app.services.profile.generator import ProfileGenerator
from app.repositories.profile import profile_repo
import logging

router = APIRouter(prefix="/api/profiles", tags=["profiles"])
logger = logging.getLogger("learnlens.api")

# Maintain backward compatibility with the old frontend endpoint:
@router.post("/extract", response_model=LearnerProfileSchema)
def extract_profile(request: ChatRequest, db: Session = Depends(get_db)):
    logger.info(f"Extracting profile for session {request.session_id}")
    try:
        # Extract profile from conversation history
        profile_schema = ProfileGenerator.extract_profile(request.history, request.message)
        
        # Persist it in the database
        db_profile = profile_repo.create_from_schema(db, profile_schema)
        logger.info(f"Profile {db_profile.id} created successfully")
        
        return profile_schema
        
    except Exception as e:
        logger.exception("Failed to extract profile")
        raise HTTPException(status_code=500, detail=f"Failed to extract profile: {str(e)}")
