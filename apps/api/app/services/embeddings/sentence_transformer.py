from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from .base import EmbeddingService
from .batching import batch_iterable
import torch

class SentenceTransformerService(EmbeddingService):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", batch_size: int = 32):
        self._model_name = model_name
        self._batch_size = batch_size
        # Use CPU by default for stability unless GPU is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(model_name, device=device)
        # Warmup
        self.model.encode(["warmup"])
        
    @property
    def model_name(self) -> str:
        return self._model_name
        
    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()
        
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # sentence_transformers is synchronous, in a real async backend we'd use asyncio.to_thread
        # but for this script we can run it directly or wrap in to_thread
        import asyncio
        loop = asyncio.get_running_loop()
        
        all_embeddings = []
        for batch in batch_iterable(texts, self._batch_size):
            embeddings = await loop.run_in_executor(
                None, 
                lambda b: self.model.encode(b, convert_to_numpy=True), 
                batch
            )
            all_embeddings.extend(embeddings.tolist())
            
        return all_embeddings

    async def embed_query(self, text: str) -> List[float]:
        import asyncio
        loop = asyncio.get_running_loop()
        embedding = await loop.run_in_executor(
            None,
            lambda t: self.model.encode(t, convert_to_numpy=True),
            text
        )
        return embedding.tolist()
