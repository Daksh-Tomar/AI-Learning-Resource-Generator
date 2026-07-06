from typing import Protocol, List, Optional
from app.schemas.ingestion import (
    ProviderCapabilities,
    ResourceCandidate,
    ResourceMetadata,
    ResourceEngagement,
    TranscriptTrack,
    TranscriptResult,
    CommentDTO
)

class ResourceProvider(Protocol):
    @property
    def provider_name(self) -> str:
        ...

    @property
    def capabilities(self) -> ProviderCapabilities:
        ...

    async def search(self, query: str, limit: int) -> List[ResourceCandidate]:
        ...

    async def fetch_metadata(self, external_ids: List[str]) -> List[ResourceMetadata]:
        ...

    async def fetch_engagement_data(self, external_ids: List[str]) -> List[ResourceEngagement]:
        ...

class TranscriptProvider(Protocol):
    async def list_tracks(self, external_id: str) -> List[TranscriptTrack]:
        ...

    async def fetch_transcript(self, external_id: str, language_code: str) -> TranscriptResult:
        ...

class CommentProvider(Protocol):
    async def fetch_comments(self, external_id: str, limit: int, order_mode: str = "TOP") -> List[CommentDTO]:
        ...
