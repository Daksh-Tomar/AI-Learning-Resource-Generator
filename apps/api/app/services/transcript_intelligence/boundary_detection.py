import numpy as np
from typing import List, Tuple
from pydantic import BaseModel

class BoundaryDetector:
    def __init__(self, similarity_threshold: float = 0.5, pause_threshold_seconds: float = 3.0):
        self.similarity_threshold = similarity_threshold
        self.pause_threshold_seconds = pause_threshold_seconds

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        a_arr = np.array(a)
        b_arr = np.array(b)
        if np.linalg.norm(a_arr) == 0 or np.linalg.norm(b_arr) == 0:
            return 0.0
        return np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr))

    def detect_boundaries(
        self, 
        segments: List[BaseModel], 
        embeddings: List[List[float]] = None
    ) -> List[bool]:
        """
        Returns a boolean array of same length as segments.
        True means the segment starts a NEW chunk (boundary before it).
        The first segment is always True.
        """
        if not segments:
            return []
            
        boundaries = [True] # First segment is always a boundary
        
        for i in range(1, len(segments)):
            prev_seg = segments[i-1]
            curr_seg = segments[i]
            
            is_boundary = False
            
            # Check pause heuristic
            if curr_seg.start_time - prev_seg.end_time > self.pause_threshold_seconds:
                is_boundary = True
                
            # Check embedding similarity if provided
            elif embeddings and i < len(embeddings):
                sim = self.cosine_similarity(embeddings[i-1], embeddings[i])
                if sim < self.similarity_threshold:
                    is_boundary = True
                    
            boundaries.append(is_boundary)
            
        return boundaries
