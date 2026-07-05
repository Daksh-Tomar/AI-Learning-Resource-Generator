from pydantic import BaseModel
from typing import Optional

class ResourceCandidate(BaseModel):
    external_id: str
    provider: str
    resource_type: str
    title: str
    description: Optional[str] = None
    creator_name: Optional[str] = None
    url: str
