import hashlib

from app.config import settings
from app.embeddings.provider import EmbeddingProvider


class LocalStubEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dim: int | None = None) -> None:
        self.dim = dim or settings.embedding_dim

    def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = []
        for i in range(self.dim):
            values.append(digest[i % len(digest)] / 255.0)
        return values
