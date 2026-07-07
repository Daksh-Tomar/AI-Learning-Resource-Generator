from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.models.chunk_embedding import ChunkEmbeddingModel
from app.models.transcript import TranscriptChunkModel
from app.schemas.retrieval import RetrievalCandidate, RetrievalScores
from app.services.embeddings.factory import EmbeddingFactory
import asyncio

class DenseRetriever:
    def __init__(self, db: Session, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.db = db
        self.embedding_service = EmbeddingFactory.get_service(model_name)
        self.model_name = model_name

    async def retrieve(
        self, 
        query: str, 
        top_k: int = 20, 
        resource_id_filter: Optional[str] = None
    ) -> List[RetrievalCandidate]:
        # 1. Embed query
        query_embedding = await self.embedding_service.embed_query(query)

        # 2. Vector search using pgvector Cosine Distance operator (<=>)
        # Cosine distance = 1 - cosine similarity
        stmt = (
            select(
                TranscriptChunkModel,
                ChunkEmbeddingModel.embedding.cosine_distance(query_embedding).label("distance")
            )
            .join(ChunkEmbeddingModel, TranscriptChunkModel.id == ChunkEmbeddingModel.chunk_id)
            .filter(ChunkEmbeddingModel.model_name == self.model_name)
        )
        
        if resource_id_filter:
            stmt = stmt.filter(TranscriptChunkModel.resource_id == resource_id_filter)
            
        stmt = stmt.order_by("distance").limit(top_k)
        
        results = self.db.execute(stmt).all()
        
        candidates = []
        for row in results:
            chunk = row[0]
            distance = row[1]
            similarity = 1.0 - float(distance)
            
            candidate = RetrievalCandidate(
                chunk_id=chunk.id,
                resource_id=chunk.resource_id,
                start_seconds=chunk.start_seconds,
                end_seconds=chunk.end_seconds,
                text=chunk.text,
                scores=RetrievalScores(dense_similarity=similarity)
            )
            candidates.append(candidate)
            
        return candidates
