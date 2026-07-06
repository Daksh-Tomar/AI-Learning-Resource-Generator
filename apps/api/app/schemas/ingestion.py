from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class ProviderCapabilities(BaseModel):
    search: bool
    metadata: bool
    engagement_metrics: bool
    transcripts: bool
    comments: bool

class ResourceCandidate(BaseModel):
    external_id: str
    title: str
    url: str
    description: Optional[str] = None
    creator_name: Optional[str] = None
    published_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None

class ResourceMetadata(BaseModel):
    external_id: str
    title: str
    description: Optional[str] = None
    creator_name: Optional[str] = None
    published_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    language: Optional[str] = None
    caption_available: Optional[bool] = None

class ResourceEngagement(BaseModel):
    external_id: str
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None

class TranscriptSegmentDTO(BaseModel):
    start_seconds: float
    duration_seconds: float
    text: str

class TranscriptResult(BaseModel):
    external_id: str
    language: str
    source_type: str
    segments: List[TranscriptSegmentDTO]
    is_generated: bool = False

class TranscriptTrack(BaseModel):
    language_code: str
    language_name: str
    is_generated: bool
    is_translatable: bool

class CommentDTO(BaseModel):
    external_comment_id: str
    text: str
    like_count: Optional[int] = 0
    published_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    reply_count: Optional[int] = 0
    is_reply: bool = False

class IngestionProgress(BaseModel):
    completed: int = 0
    failed: int = 0
    skipped: int = 0

class IngestionSummary(BaseModel):
    search_session_id: UUID
    status: str
    total_resources: int
    metadata: IngestionProgress
    transcripts: IngestionProgress
    comments: IngestionProgress
    metrics: IngestionProgress
