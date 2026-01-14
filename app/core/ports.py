from typing import Protocol

from app.core.domain import AtlasLink, AtlasNode


class AtlasRepository(Protocol):
    def get_by_idempotency_key(self, idempotency_key: str) -> AtlasNode | None: ...

    def create_staged_node(
        self,
        idempotency_key: str,
        title: str,
        principle: str,
        evidence: str | None,
        confidence: int,
        last_verified,
        links: list[AtlasLink],
    ) -> AtlasNode: ...

    def mark_committed(self, node_id: str) -> AtlasNode: ...

    def get_by_id(self, node_id: str) -> AtlasNode | None: ...

    def get_links(self, node_id: str) -> list[AtlasLink]: ...


class GraphRepository(Protocol):
    def upsert_node(self, node: AtlasNode, links: list[AtlasLink]) -> None: ...


class VectorRepository(Protocol):
    def upsert_node(self, node: AtlasNode) -> None: ...
    def search(self, query: str, k: int) -> list[dict]: ...


class NotionRepository(Protocol):
    def mirror_node(self, node: AtlasNode, links: list[AtlasLink]) -> None: ...


class AuditRepository(Protocol):
    def log(
        self,
        action: str,
        entity_type: str,
        entity_id: str | None,
        idempotency_key: str,
        status: str,
        message: str | None = None,
    ) -> None: ...
