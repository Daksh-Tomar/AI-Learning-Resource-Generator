from typing import Protocol, List
from pydantic import BaseModel
from typing import Optional

class ChunkData(BaseModel):
    chunk_index: int
    text: str
    start_seconds: Optional[float] = None
    end_seconds: Optional[float] = None
    start_segment_index: Optional[int] = None
    end_segment_index: Optional[int] = None
    token_count: Optional[int] = None

class TranscriptChunker(Protocol):
    
    @property
    def version(self) -> str:
        """Return a version string identifying the chunking algorithm."""
        ...
        
    @property
    def config_hash(self) -> str:
        """Return a hash representing the current configuration of the chunker."""
        ...

    def chunk_segments(self, segments: List[BaseModel]) -> List[ChunkData]:
        """
        Chunk a list of transcript segments into a list of chunks.
        Segments are expected to conform to the preprocessing SegmentData schema.
        """
        ...
