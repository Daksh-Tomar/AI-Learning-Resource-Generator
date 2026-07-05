from enum import Enum
from pydantic import BaseModel, Field, model_validator
from typing import Optional

class SkillLevel(str, Enum):
    complete_beginner = "complete_beginner"
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class LearningFormat(str, Enum):
    video = "video"
    written = "written"
    project_based = "project_based"
    mixed = "mixed"

class LearnerProfileSchema(BaseModel):
    subject: str = Field(min_length=2, max_length=150)
    goal: str = Field(min_length=2, max_length=250)
    current_level: SkillLevel
    target_level: Optional[SkillLevel] = None
    deadline_days: int = Field(gt=0, le=3650)
    daily_hours: float = Field(gt=0, le=24)
    known_topics: list[str] = Field(default_factory=list)
    weak_topics: list[str] = Field(default_factory=list)
    preferred_formats: list[LearningFormat] = Field(default_factory=list)
    preferred_language: Optional[str] = None
    wants_projects: bool = False
    wants_interview_prep: bool = False

    @model_validator(mode='after')
    def validate_topics(self) -> 'LearnerProfileSchema':
        # Normalize topics (lowercase, strip whitespace)
        self.known_topics = list(set([t.strip().lower() for t in self.known_topics if t.strip()]))
        self.weak_topics = list(set([t.strip().lower() for t in self.weak_topics if t.strip()]))
        
        # Check for overlaps
        overlap = set(self.known_topics).intersection(set(self.weak_topics))
        if overlap:
            raise ValueError(f"Topics cannot be both known and weak: {overlap}")
        
        return self

    @property
    def total_available_hours(self) -> float:
        return self.deadline_days * self.daily_hours
