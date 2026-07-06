from datetime import datetime
import isodate
from typing import List, Optional
from app.schemas.ingestion import (
    ResourceCandidate,
    ResourceMetadata,
    ResourceEngagement,
    CommentDTO
)
from .types import (
    YouTubeSearchResponse,
    YouTubeVideoResponse,
    YouTubeCommentThreadResponse
)

class YouTubeMapper:
    @staticmethod
    def _parse_datetime(dt_str: str) -> Optional[datetime]:
        try:
            return isodate.parse_datetime(dt_str) if dt_str else None
        except Exception:
            return None

    @staticmethod
    def _parse_duration(duration_str: str) -> Optional[int]:
        try:
            if not duration_str:
                return None
            return int(isodate.parse_duration(duration_str).total_seconds())
        except Exception:
            return None

    @classmethod
    def map_search_response(cls, response: YouTubeSearchResponse) -> List[ResourceCandidate]:
        candidates = []
        for item in response.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            if not video_id:
                continue
            
            snippet = item.get("snippet", {})
            candidates.append(ResourceCandidate(
                external_id=video_id,
                title=snippet.get("title", ""),
                url=f"https://www.youtube.com/watch?v={video_id}",
                description=snippet.get("description", ""),
                creator_name=snippet.get("channelTitle", ""),
                published_at=cls._parse_datetime(snippet.get("publishedAt", "")),
                duration_seconds=None # Not available in search response
            ))
        return candidates

    @classmethod
    def map_video_metadata(cls, response: YouTubeVideoResponse) -> List[ResourceMetadata]:
        metadata_list = []
        for item in response.get("items", []):
            video_id = item.get("id")
            if not video_id:
                continue
                
            snippet = item.get("snippet", {})
            content_details = item.get("contentDetails", {})
            
            metadata_list.append(ResourceMetadata(
                external_id=video_id,
                title=snippet.get("title", ""),
                description=snippet.get("description", ""),
                creator_name=snippet.get("channelTitle", ""),
                published_at=cls._parse_datetime(snippet.get("publishedAt", "")),
                duration_seconds=cls._parse_duration(content_details.get("duration", "")),
                language=snippet.get("defaultAudioLanguage"),
                caption_available=content_details.get("caption") == "true"
            ))
        return metadata_list

    @classmethod
    def map_video_engagement(cls, response: YouTubeVideoResponse) -> List[ResourceEngagement]:
        engagement_list = []
        for item in response.get("items", []):
            video_id = item.get("id")
            if not video_id:
                continue
                
            stats = item.get("statistics", {})
            
            engagement_list.append(ResourceEngagement(
                external_id=video_id,
                view_count=int(stats.get("viewCount")) if stats.get("viewCount") else 0,
                like_count=int(stats.get("likeCount")) if stats.get("likeCount") else None,
                comment_count=int(stats.get("commentCount")) if stats.get("commentCount") else None
            ))
        return engagement_list

    @classmethod
    def map_comment_threads(cls, response: YouTubeCommentThreadResponse) -> List[CommentDTO]:
        comments = []
        for item in response.get("items", []):
            top_level_comment = item.get("snippet", {}).get("topLevelComment", {})
            snippet = top_level_comment.get("snippet", {})
            
            comment_id = top_level_comment.get("id")
            if not comment_id:
                continue
                
            comments.append(CommentDTO(
                external_comment_id=comment_id,
                text=snippet.get("textOriginal", ""),
                like_count=snippet.get("likeCount", 0),
                published_at=cls._parse_datetime(snippet.get("publishedAt", "")),
                updated_at=cls._parse_datetime(snippet.get("updatedAt", "")),
                reply_count=item.get("snippet", {}).get("totalReplyCount", 0),
                is_reply=False
            ))
        return comments
