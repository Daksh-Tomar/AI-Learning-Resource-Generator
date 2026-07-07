import re
from typing import Dict, List

class LexicalFeatures:
    def __init__(self):
        # A simple list of advanced technical terms that imply higher difficulty
        self.advanced_terms = ["asynchronous", "polymorphism", "eigenvalue", "tensor", "monad", "gradient descent", "backpropagation"]

    def extract(self, text: str) -> Dict[str, float]:
        text_lower = text.lower()
        word_count = len(text_lower.split())
        if word_count == 0:
            return {"technical_density": 0.0}
            
        advanced_count = sum(1 for term in self.advanced_terms if term in text_lower)
        
        return {
            "technical_density": min(1.0, (advanced_count * 10) / word_count)
        }
