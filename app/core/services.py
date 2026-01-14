from dataclasses import dataclass

from app.core.domain import AtlasLink, AtlasNode
from app.core.ports import (
    AtlasRepository,
    AuditRepository,
    GraphRepository,
    NotionRepository,
    VectorRepository,
)


class NotFoundError(Exception):
    pass


@dataclass
class StageService:
    atlas_repo: AtlasRepository
    audit_repo: AuditRepository

    def stage(
        self,
        idempotency_key: str,
        title: str,
        principle: str,
        evidence: str | None,
        confidence: int,
        last_verified,
        links: list[AtlasLink],
    ) -> AtlasNode:
        existing = self.atlas_repo.get_by_idempotency_key(idempotency_key)
        if existing:
            self.audit_repo.log(
                action="stage",
                entity_type="atlas_node",
                entity_id=existing.id,
                idempotency_key=idempotency_key,
                status="noop",
                message="idempotent replay",
            )
            return existing
        node = self.atlas_repo.create_staged_node(
            idempotency_key=idempotency_key,
            title=title,
            principle=principle,
            evidence=evidence,
            confidence=confidence,
            last_verified=last_verified,
            links=links,
        )
        self.audit_repo.log(
            action="stage",
            entity_type="atlas_node",
            entity_id=node.id,
            idempotency_key=idempotency_key,
            status="success",
        )
        return node


@dataclass
class CommitService:
    atlas_repo: AtlasRepository
    graph_repo: GraphRepository
    vector_repo: VectorRepository
    audit_repo: AuditRepository
    notion_repo: NotionRepository | None = None

    def commit(self, idempotency_key: str) -> AtlasNode:
        node = self.atlas_repo.get_by_idempotency_key(idempotency_key)
        if not node:
            raise NotFoundError("staged node not found")
        if node.status == "committed":
            self.audit_repo.log(
                action="commit",
                entity_type="atlas_node",
                entity_id=node.id,
                idempotency_key=idempotency_key,
                status="noop",
                message="already committed",
            )
            return node
        node = self.atlas_repo.mark_committed(node.id)
        links = self.atlas_repo.get_links(node.id)
        self.audit_repo.log(
            action="commit",
            entity_type="atlas_node",
            entity_id=node.id,
            idempotency_key=idempotency_key,
            status="success",
        )
        try:
            self.graph_repo.upsert_node(node, links)
            self.audit_repo.log(
                action="graph_update",
                entity_type="atlas_node",
                entity_id=node.id,
                idempotency_key=idempotency_key,
                status="success",
            )
        except Exception as exc:
            self.audit_repo.log(
                action="graph_update",
                entity_type="atlas_node",
                entity_id=node.id,
                idempotency_key=idempotency_key,
                status="error",
                message=str(exc),
            )
            raise
        try:
            self.vector_repo.upsert_node(node)
            self.audit_repo.log(
                action="vector_upsert",
                entity_type="atlas_node",
                entity_id=node.id,
                idempotency_key=idempotency_key,
                status="success",
            )
        except Exception as exc:
            self.audit_repo.log(
                action="vector_upsert",
                entity_type="atlas_node",
                entity_id=node.id,
                idempotency_key=idempotency_key,
                status="error",
                message=str(exc),
            )
            raise
        if self.notion_repo:
            try:
                self.notion_repo.mirror_node(node, links)
                self.audit_repo.log(
                    action="notion_mirror",
                    entity_type="atlas_node",
                    entity_id=node.id,
                    idempotency_key=idempotency_key,
                    status="success",
                )
            except Exception as exc:
                self.audit_repo.log(
                    action="notion_mirror",
                    entity_type="atlas_node",
                    entity_id=node.id,
                    idempotency_key=idempotency_key,
                    status="error",
                    message=str(exc),
                )
                raise
        return node


@dataclass
class SearchService:
    vector_repo: VectorRepository

    def search(self, query: str, k: int) -> list[dict]:
        return self.vector_repo.search(query=query, k=k)
