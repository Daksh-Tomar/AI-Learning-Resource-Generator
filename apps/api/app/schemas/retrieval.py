from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class RetrievalScores(BaseModel):
    dense_similarity: Optional[float] = None
    lexical_score: Optional[float] = None
    rrf_score: Optional[float] = None
    reranker_score: Optional[float] = None

class RetrievalRanks(BaseModel):
    dense_rank: Optional[int] = None
    lexical_rank: Optional[int] = None
    fusion_rank: Optional[int] = None
    final_rank: Optional[int] = None

class RetrievalCandidate(BaseModel):
    chunk_id: UUID
    resource_id: UUID
    start_seconds: Optional[float] = None
    end_seconds: Optional[float] = None
    text: str
    scores: RetrievalScores = Field(default_factory=RetrievalScores)
    ranks: RetrievalRanks = Field(default_factory=RetrievalRanks)

class RerankedCandidate(RetrievalCandidate):
    pass
