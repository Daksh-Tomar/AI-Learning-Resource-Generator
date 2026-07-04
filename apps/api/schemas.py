from pydantic import BaseModel, Field
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str
    message: str
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    session_id: str
    message: str

class LearnerProfileSchema(BaseModel):
    goal: Optional[str] = Field(None, description="The primary goal of the learner (e.g. software engineering placement)")
    subject: Optional[str] = Field(None, description="The specific subject they want to learn (e.g. dynamic programming)")
    current_level: Optional[str] = Field(None, description="Current knowledge level (e.g. beginner, intermediate)")
    target_level: Optional[str] = Field(None, description="The desired knowledge level")
    deadline_days: Optional[int] = Field(None, description="Number of days available for study")
    daily_hours: Optional[float] = Field(None, description="Hours available per day")
    preferred_language: Optional[str] = Field(None, description="Language preference for content")
    content_preference: List[str] = Field(default_factory=list, description="List of preferred formats (e.g. visual explanations, problem solving)")
    known_topics: List[str] = Field(default_factory=list, description="List of topics the user already knows")
    weak_topics: List[str] = Field(default_factory=list, description="List of topics the user struggles with")
