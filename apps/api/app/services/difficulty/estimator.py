from typing import Dict, Any
from .lexical_features import LexicalFeatures
from .prerequisite_features import PrerequisiteFeatures

class DifficultyEstimator:
    def __init__(self):
        self.lexical = LexicalFeatures()
        self.prereq = PrerequisiteFeatures()
        
    def estimate(self, text: str) -> Dict[str, Any]:
        lex_features = self.lexical.extract(text)
        pre_features = self.prereq.extract(text)
        
        # Merge features
        features = {**lex_features, **pre_features}
        
        # Simple heuristic for difficulty level
        score = features.get("technical_density", 0) + features.get("has_prerequisites", 0) * 0.5
        
        if score > 0.8:
            level = "ADVANCED"
        elif score > 0.3:
            level = "INTERMEDIATE"
        else:
            level = "BEGINNER"
            
        return {
            "estimated_level": level,
            "confidence": 0.6,
            "feature_values": features,
            "feature_extractor_version": "v1",
            "estimator_version": "v1"
        }
