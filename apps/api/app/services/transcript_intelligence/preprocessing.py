import re
from typing import List
from pydantic import BaseModel

class SegmentData(BaseModel):
    index: int
    text: str
    start_time: float
    end_time: float

class Preprocessor:
    def __init__(self):
        # Basic regex to replace multiple spaces with single space
        self.whitespace_re = re.compile(r'\s+')
        
    def normalize_text(self, text: str) -> str:
        text = text.strip()
        text = self.whitespace_re.sub(' ', text)
        # Fix missing spaces after punctuation
        text = re.sub(r'([.?!,;])([A-Za-z])', r'\1 \2', text)
        # Example specific normalization: "e. g." -> "e.g."
        text = text.replace("e. g.", "e.g.")
        text = text.replace("i. e.", "i.e.")
        return text

    def preprocess_segments(self, segments: List[SegmentData]) -> List[SegmentData]:
        processed = []
        for seg in segments:
            normalized_text = self.normalize_text(seg.text)
            if normalized_text: # Filter out empty segments
                processed.append(SegmentData(
                    index=seg.index,
                    text=normalized_text,
                    start_time=seg.start_time,
                    end_time=seg.end_time
                ))
        return processed
