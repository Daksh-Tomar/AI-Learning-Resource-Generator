from typing import Protocol

class EmbeddingService(Protocol):

    @property
    def model_name(self) -> str:
        ...

    @property
    def dimension(self) -> int:
        ...

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        ...

    async def embed_query(self, text: str) -> list[float]:
        ...
