from sqlalchemy.orm import Session
from typing import Optional
from app.repositories.base import BaseRepository
from app.models.learner_profile import LearnerProfileModel
from app.schemas.learner_profile import LearnerProfileSchema

class ProfileRepository(BaseRepository[LearnerProfileModel]):
    def __init__(self):
        super().__init__(LearnerProfileModel)

    def create_from_schema(self, db: Session, schema: LearnerProfileSchema, conversation_id: Optional[str] = None) -> LearnerProfileModel:
        # Convert schema to dict, enum to value
        obj_in = schema.model_dump()
        
        # Enums are automatically converted to strings in model_dump if we configured it, but just in case:
        obj_in["current_level"] = obj_in["current_level"].value if hasattr(obj_in["current_level"], "value") else obj_in["current_level"]
        if obj_in.get("target_level"):
            obj_in["target_level"] = obj_in["target_level"].value if hasattr(obj_in["target_level"], "value") else obj_in["target_level"]
        obj_in["preferred_formats"] = [f.value if hasattr(f, "value") else f for f in obj_in["preferred_formats"]]

        if conversation_id:
            obj_in["conversation_id"] = conversation_id
            
        return self.create(db, obj_in)

profile_repo = ProfileRepository()
