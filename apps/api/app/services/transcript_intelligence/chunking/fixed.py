from typing import List, Optional
import tiktoken
import hashlib
import json
from pydantic import BaseModel
from .base import TranscriptChunker, ChunkData

class FixedTokenChunker(TranscriptChunker):
    """
    Groups sequential segments into chunks based on a fixed token count and overlap.
    """
    def __init__(self, target_tokens: int = 500, overlap_tokens: int = 50, encoding_name: str = "cl100k_base"):
        self.target_tokens = target_tokens
        self.overlap_tokens = overlap_tokens
        self.encoding_name = encoding_name
        self.tokenizer = tiktoken.get_encoding(encoding_name)
        
    @property
    def version(self) -> str:
        return "fixed_token_v1"
        
    @property
    def config_hash(self) -> str:
        config = {
            "target_tokens": self.target_tokens,
            "overlap_tokens": self.overlap_tokens,
            "encoding": self.encoding_name
        }
        return hashlib.md5(json.dumps(config, sort_keys=True).encode()).hexdigest()

    def _count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def chunk_segments(self, segments: List[BaseModel]) -> List[ChunkData]:
        # segments is expected to be a list of objects with text, index, start_time, end_time
        chunks = []
        current_chunk_index = 0
        
        i = 0
        while i < len(segments):
            chunk_segments = []
            chunk_tokens = 0
            
            # Forward accumulation
            while i < len(segments):
                seg = segments[i]
                seg_tokens = self._count_tokens(seg.text)
                
                # If adding this segment exceeds target, and we already have some segments, break
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
            
            # Calculate overlap for next chunk
            # Step backwards from the last added segment to satisfy overlap_tokens
            if i >= len(segments):
                break
                
            overlap_acc = 0
            back_step = i - 1
            while back_step >= 0 and overlap_acc < self.overlap_tokens:
                seg_tokens = self._count_tokens(segments[back_step].text)
                overlap_acc += seg_tokens
                if overlap_acc >= self.overlap_tokens and back_step < i - 1:
                    # don't overlap exactly everything if one segment is huge, but ensure some progress
                    pass
                back_step -= 1
            
            # Next iteration starts at the overlapping segment index
            # Ensure we always make forward progress
            next_start = back_step + 1
            if next_start >= i:
                next_start = i - 1 # At least overlap 1 segment if possible
            i = max(next_start, 0)
            
            # If the next start is somehow exactly where we ended before overlap, prevent infinite loop:
            # Actually, the logic above ensures i will be less than the original i (since next_start <= i - 1), 
            # so we overlap backwards. Wait, if we overlap backwards, the next forward pass might just collect the exact same segments if the first segment is larger than target_tokens.
            # To prevent infinite loop if a single segment is huge:
            # We must guarantee `i` advances compared to the start of the current chunk.
            original_start = chunk_segments[0].index
            if i <= original_start:
                i = original_start + 1

        return chunks
