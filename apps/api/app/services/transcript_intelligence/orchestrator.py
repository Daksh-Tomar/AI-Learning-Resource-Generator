import hashlib
from typing import List, Any
from sqlalchemy.orm import Session
from app.models.transcript import TranscriptChunkModel, TranscriptSegmentModel
from app.models.chunk_embedding import ChunkEmbeddingModel
from .preprocessing import Preprocessor, SegmentData
from .chunking.semantic import SemanticChunker
from .boundary_detection import BoundaryDetector
from app.services.embeddings.factory import EmbeddingFactory

class TranscriptOrchestrator:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.preprocessor = Preprocessor()
        self.boundary_detector = BoundaryDetector()
        self.chunker = SemanticChunker(boundary_detector=self.boundary_detector)
        self.embedding_service = EmbeddingFactory.get_service()

    async def process_transcript(self, transcript_id: str, resource_id: str):
        # 1. Load raw segments
        raw_segments = self.db.query(TranscriptSegmentModel).filter(
            TranscriptSegmentModel.transcript_id == transcript_id
        ).order_by(TranscriptSegmentModel.start_time).all()

        if not raw_segments:
            return []

        # 2. Preprocess
        segments_data = [
            SegmentData(
                index=s.index,
                text=s.text,
                start_time=s.start_time,
                end_time=s.end_time
            ) for s in raw_segments
        ]
        processed_segments = self.preprocessor.preprocess_segments(segments_data)

        # 3. Optional: First pass embeddings for semantic boundaries
        # For simplicity, we'll just use pause heuristic boundary detection first
        
        # 4. Chunk
        chunks_data = self.chunker.chunk_segments(processed_segments)

        # 5. Persist chunks
        saved_chunks = []
        for chunk_data in chunks_data:
            content_hash = hashlib.md5(chunk_data.text.encode()).hexdigest()
            
            # Check if exists
            existing_chunk = self.db.query(TranscriptChunkModel).filter(
                TranscriptChunkModel.transcript_id == transcript_id,
                TranscriptChunkModel.chunking_version == self.chunker.version,
                TranscriptChunkModel.chunking_config_hash == self.chunker.config_hash,
                TranscriptChunkModel.chunk_index == chunk_data.chunk_index
            ).first()

            if not existing_chunk:
                existing_chunk = TranscriptChunkModel(
                    transcript_id=transcript_id,
                    resource_id=resource_id,
                    chunk_index=chunk_data.chunk_index,
                    text=chunk_data.text,
                    start_seconds=chunk_data.start_seconds,
                    end_seconds=chunk_data.end_seconds,
                    start_segment_index=chunk_data.start_segment_index,
                    end_segment_index=chunk_data.end_segment_index,
                    token_count=chunk_data.token_count,
                    chunking_version=self.chunker.version,
                    chunking_config_hash=self.chunker.config_hash,
                    content_hash=content_hash
                )
                self.db.add(existing_chunk)
                self.db.flush() # get ID
            
            saved_chunks.append(existing_chunk)
            
        self.db.commit()

        # 6. Embed chunks
        texts_to_embed = [c.text for c in saved_chunks]
        embeddings = await self.embedding_service.embed_documents(texts_to_embed)

        for chunk, embedding in zip(saved_chunks, embeddings):
            # Check if embedding already exists
            existing_embedding = self.db.query(ChunkEmbeddingModel).filter(
                ChunkEmbeddingModel.chunk_id == chunk.id,
                ChunkEmbeddingModel.model_name == self.embedding_service.model_name
            ).first()

            if not existing_embedding:
                new_embedding = ChunkEmbeddingModel(
                    chunk_id=chunk.id,
                    model_name=self.embedding_service.model_name,
                    model_version="1.0", # Could pull from service
                    embedding_dimension=self.embedding_service.dimension,
                    embedding=embedding,
                    content_hash=chunk.content_hash
                )
                self.db.add(new_embedding)
        
        self.db.commit()
        return saved_chunks
