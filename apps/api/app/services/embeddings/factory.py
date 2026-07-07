from typing import Dict, Any
from .base import EmbeddingService
from .sentence_transformer import SentenceTransformerService

class EmbeddingFactory:
    _instances: Dict[str, EmbeddingService] = {}

    @classmethod
    def get_service(cls, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", **kwargs: Any) -> EmbeddingService:
        if model_name not in cls._instances:
            # Expand with more providers as needed
            cls._instances[model_name] = SentenceTransformerService(model_name=model_name, **kwargs)
        return cls._instances[model_name]
