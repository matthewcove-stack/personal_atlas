from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.config import settings
from app.core.domain import AtlasNode
from app.embeddings.provider import EmbeddingProvider


class QdrantVectorRepository:
    def __init__(self, embedding_provider: EmbeddingProvider) -> None:
        self._client = QdrantClient(url=settings.qdrant_url)
        self._provider = embedding_provider
        self._collection = "atlas_nodes"
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        collections = self._client.get_collections().collections
        names = {c.name for c in collections}
        if self._collection in names:
            return
        self._client.create_collection(
            collection_name=self._collection,
            vectors_config=qmodels.VectorParams(
                size=settings.embedding_dim, distance=qmodels.Distance.COSINE
            ),
        )

    def upsert_node(self, node: AtlasNode) -> None:
        vector = self._provider.embed(f"{node.title}\n{node.principle}\n{node.evidence or ''}")
        payload = {
            "id": node.id,
            "title": node.title,
            "principle": node.principle,
            "confidence": node.confidence,
            "last_verified": str(node.last_verified),
        }
        self._client.upsert(
            collection_name=self._collection,
            points=[
                qmodels.PointStruct(
                    id=node.id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )

    def search(self, query: str, k: int) -> list[dict]:
        vector = self._provider.embed(query)
        results = self._client.search(
            collection_name=self._collection,
            query_vector=vector,
            limit=k,
        )
        output = []
        for r in results:
            payload = r.payload or {}
            output.append(
                {
                    "id": payload.get("id", r.id),
                    "score": r.score,
                    "title": payload.get("title", ""),
                    "principle": payload.get("principle", ""),
                }
            )
        return output
