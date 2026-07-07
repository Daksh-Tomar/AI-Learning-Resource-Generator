from typing import List, Optional
import tiktoken
import hashlib
import json
from pydantic import BaseModel
from .base import TranscriptChunker, ChunkData
from ..boundary_detection import BoundaryDetector

class SemanticChunker(TranscriptChunker):
    """
    Groups sequential segments into chunks using semantic boundaries (pauses, similarity)
    while strictly enforcing min and max token constraints.
    """
    def __init__(self, 
                 min_tokens: int = 150, 
                 target_tokens: int = 400, 
                 max_tokens: int = 700, 
                 overlap_tokens: int = 50,
                 encoding_name: str = "cl100k_base",
                 boundary_detector: Optional[BoundaryDetector] = None):
        self.min_tokens = min_tokens
        self.target_tokens = target_tokens
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.encoding_name = encoding_name
        self.tokenizer = tiktoken.get_encoding(encoding_name)
        self.boundary_detector = boundary_detector or BoundaryDetector()
        
    @property
    def version(self) -> str:
        return "semantic_chunker_v1"
        
    @property
    def config_hash(self) -> str:
        config = {
            "min_tokens": self.min_tokens,
            "target_tokens": self.target_tokens,
            "max_tokens": self.max_tokens,
            "overlap_tokens": self.overlap_tokens,
            "encoding": self.encoding_name,
            "sim_threshold": self.boundary_detector.similarity_threshold,
            "pause_threshold": self.boundary_detector.pause_threshold_seconds
        }
        return hashlib.md5(json.dumps(config, sort_keys=True).encode()).hexdigest()

    def _count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def chunk_segments(self, segments: List[BaseModel], embeddings: List[List[float]] = None) -> List[ChunkData]:
        if not segments:
            return []
            
        boundaries = self.boundary_detector.detect_boundaries(segments, embeddings)
        
        chunks = []
        current_chunk_index = 0
        
        i = 0
        while i < len(segments):
            chunk_segments = []
            chunk_tokens = 0
            
            # Start accumulating
            while i < len(segments):
                seg = segments[i]
                seg_tokens = self._count_tokens(seg.text)
                
                # Enforce max constraint strictly
                if chunk_tokens + seg_tokens > self.max_tokens and len(chunk_segments) > 0:
                    break
                    
                # If we passed min_tokens and hit a natural boundary, we can stop here
                if chunk_tokens >= self.min_tokens and boundaries[i] and len(chunk_segments) > 0:
                    break
                    
                # If we passed target_tokens (even without a boundary), it's getting too long, stop.
                if chunk_tokens + seg_tokens > self.target_tokens and len(chunk_segments) > 0:
                    break
                    
                chunk_segments.append(seg)
                chunk_tokens += seg_tokens
                i += 1
                
            if not chunk_segments:
                break
                
            # Emit chunk
            chunk_text = " ".join([s.text for s in chunk_segments])
            chunks.append(ChunkData(
                chunk_index=current_chunk_index,
                text=chunk_text,
                start_seconds=chunk_segments[0].start_time,
                end_seconds=chunk_segments[-1].end_time,
                start_segment_index=chunk_segments[0].index,
                end_segment_index=chunk_segments[-1].index,
                token_count=chunk_tokens
            ))
            current_chunk_index += 1
            
            # Step back for overlap
            if i >= len(segments):
                break
                
            overlap_acc = 0
            back_step = i - 1
            while back_step >= 0 and overlap_acc < self.overlap_tokens:
                seg_tokens = self._count_tokens(segments[back_step].text)
                overlap_acc += seg_tokens
                back_step -= 1
                
            next_start = back_step + 1
            if next_start >= i:
                next_start = i - 1
                
            original_start = chunk_segments[0].index
            i = max(next_start, original_start + 1)

        return chunks
