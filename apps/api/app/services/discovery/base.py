from pydantic import BaseModel
from typing import List, Optional

class ResourceProvider:
    """
    Abstract base class for all external resource providers (e.g. YouTube, Coursera).
    """
    @property
    def provider_name(self) -> str:
        raise NotImplementedError

    def search(self, query: str, max_results: int = 5) -> List[dict]:
        """
        Search the provider for resources matching the query.
        Returns a list of raw resource dictionaries.
        """
        raise NotImplementedError

    def get_metadata(self, external_id: str) -> dict:
        """
        Fetch detailed metadata for a specific resource by its external ID.
        """
        raise NotImplementedError

    def get_transcript(self, external_id: str) -> Optional[str]:
        """
        Fetch the transcript/subtitles for a resource, if available.
        """
        raise NotImplementedError
