from typing import List, Optional
from app.schemas.ingestion import (
    ProviderCapabilities,
    ResourceCandidate,
    ResourceMetadata,
    ResourceEngagement,
    CommentDTO
)
from app.services.providers.interfaces import ResourceProvider, CommentProvider
from .client import YouTubeClient
from .mapper import YouTubeMapper
from .exceptions import CommentsDisabledError

class YouTubeProvider(ResourceProvider, CommentProvider):
    def __init__(self, api_key: str):
        self.client = YouTubeClient(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "YOUTUBE"

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            search=True,
            metadata=True,
            engagement_metrics=True,
            transcripts=True,
            comments=True
        )

    async def search(self, query: str, limit: int = 50) -> List[ResourceCandidate]:
        response = await self.client.search_videos(query=query, max_results=limit)
        return YouTubeMapper.map_search_response(response)

    async def fetch_metadata(self, external_ids: List[str]) -> List[ResourceMetadata]:
        if not external_ids:
            return []
        # YouTube API allows up to 50 ids per request
        response = await self.client.get_videos(video_ids=external_ids[:50])
        return YouTubeMapper.map_video_metadata(response)

    async def fetch_engagement_data(self, external_ids: List[str]) -> List[ResourceEngagement]:
        if not external_ids:
            return []
        response = await self.client.get_videos(video_ids=external_ids[:50])
        return YouTubeMapper.map_video_engagement(response)

    async def fetch_comments(self, external_id: str, limit: int = 100, order_mode: str = "relevance") -> List[CommentDTO]:
        # 'order_mode' can be "relevance" (top) or "time" (recent)
        try:
            response = await self.client.get_comment_threads(video_id=external_id, max_results=limit, order=order_mode)
            return YouTubeMapper.map_comment_threads(response)
        except Exception as e:
            if "commentsDisabled" in str(e):
                raise CommentsDisabledError("Comments are disabled for this video")
            raise e
