import httpx
from typing import Dict, Any, List
from .exceptions import (
    ProviderTimeoutError,
    ProviderServerError,
    InvalidApiKeyError,
    QuotaExceededError
)

class YouTubeClient:
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def _request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        params["key"] = self.api_key
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.BASE_URL}/{endpoint}", params=params, timeout=10.0)
                
                if response.status_code == 400:
                    data = response.json()
                    reason = data.get("error", {}).get("errors", [{}])[0].get("reason", "")
                    if reason == "keyInvalid":
                        raise InvalidApiKeyError("Invalid YouTube API Key")
                    raise ProviderServerError(f"Bad Request: {data}")
                elif response.status_code == 403:
                    data = response.json()
                    reason = data.get("error", {}).get("errors", [{}])[0].get("reason", "")
                    if reason in ("quotaExceeded", "dailyLimitExceeded"):
                        raise QuotaExceededError("YouTube API Quota Exceeded")
                    raise ProviderServerError(f"Forbidden: {data}")
                elif response.status_code >= 500:
                    raise ProviderServerError(f"YouTube Server Error: {response.status_code}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException as e:
            raise ProviderTimeoutError(str(e))
        except httpx.RequestError as e:
            raise ProviderServerError(str(e))

    async def search_videos(self, query: str, max_results: int = 50) -> Dict[str, Any]:
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results
        }
        return await self._request("search", params)

    async def get_videos(self, video_ids: List[str]) -> Dict[str, Any]:
        params = {
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(video_ids)
        }
        return await self._request("videos", params)

    async def get_comment_threads(self, video_id: str, max_results: int = 100, page_token: str = None, order: str = "relevance") -> Dict[str, Any]:
        params = {
            "part": "snippet",
            "videoId": video_id,
            "maxResults": max_results,
            "order": order
        }
        if page_token:
            params["pageToken"] = page_token
        return await self._request("commentThreads", params)
