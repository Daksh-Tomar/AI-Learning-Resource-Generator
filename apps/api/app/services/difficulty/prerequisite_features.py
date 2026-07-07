import re
from typing import Dict

class PrerequisiteFeatures:
    def __init__(self):
        self.prereq_patterns = [
            r"you should already know",
            r"assuming you are familiar with",
            r"prerequisites for this",
            r"if you haven't already, watch",
            r"this requires an understanding of"
        ]
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.prereq_patterns]

    def extract(self, text: str) -> Dict[str, float]:
        count = sum(1 for p in self.compiled_patterns if p.search(text))
        return {
            "has_prerequisites": 1.0 if count > 0 else 0.0,
            "prerequisite_density": min(1.0, count / 5.0)
        }
