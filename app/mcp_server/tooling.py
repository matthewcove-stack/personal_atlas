from dataclasses import dataclass
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from app.config import settings
from app.core.domain import AtlasLink
from app.core.services import CommitService, NotFoundError, StageService
from app.mcp_server.schemas import AtlasNodeInput

if TYPE_CHECKING:
    from app.adapters.postgres.repo import PostgresAtlasRepository, PostgresAuditRepository
    from app.adapters.postgres.staged_repo import StagedWriteRepository
    from app.adapters.qdrant.repo import QdrantVectorRepository
    from app.adapters.neo4j.repo import Neo4jGraphRepository
    from app.adapters.notion.client import NotionMirrorRepository


def _canonical_title(domain: str, subsystem: str) -> str:
    return f"{domain} / {subsystem}"


def _canonical_evidence(full_knowledge: str, evidence: str | None, tools_materials: str | None) -> str:
    parts = [f"Full knowledge: {full_knowledge}"]
    if evidence:
        parts.append(f"Evidence: {evidence}")
    if tools_materials:
        parts.append(f"Tools/materials: {tools_materials}")
    return "\n".join(parts)


def _parse_date(value: str) -> date:
    return datetime.fromisoformat(value).date()


@dataclass
class AtlasMcpTooling:
    atlas_repo: Any
    audit_repo: Any
    staged_repo: Any
    vector_repo: Any
    graph_repo: Any
    notion_repo: Any | None

    def health(self) -> dict:
        return {
            "status": "ok",
            "versions": {"mcp": "0.1.0", "api": "v1"},
        }

    def search(self, query: str, top_k: int = 5, domain: str | None = None, subsystem: str | None = None) -> dict:
        results = self.vector_repo.search(query=query, k=top_k)
        return {
            "results": results,
            "meta": {"top_k": top_k, "domain": domain, "subsystem": subsystem, "count": len(results)},
        }

    def stage_node(self, node: AtlasNodeInput) -> dict:
        existing = self.staged_repo.get_by_idempotency_key(node.idempotency_key)
        canonical_payload = {
            "commit": {
                "idempotency_key": node.idempotency_key,
                "title": _canonical_title(node.domain, node.subsystem),
                "principle": node.principle,
                "evidence": _canonical_evidence(node.full_knowledge, node.evidence, node.tools_materials),
                "confidence": node.confidence,
                "last_verified": str(node.last_verified),
                "links": [],
            },
            "meta": {
                "domain": node.domain,
                "subsystem": node.subsystem,
            },
        }
        validation_summary = {"valid": True, "errors": []}
        if existing:
            return {
                "staged_id": existing.id,
                "validation": existing.validation_summary,
                "dry_run_payload": existing.payload.get("commit"),
                "idempotency_key": existing.idempotency_key,
            }
        staged = self.staged_repo.create(
            payload=canonical_payload,
            validation_summary=validation_summary,
            idempotency_key=node.idempotency_key,
        )
        return {
            "staged_id": staged.id,
            "validation": validation_summary,
            "dry_run_payload": canonical_payload["commit"],
            "idempotency_key": node.idempotency_key,
        }

    def commit_node(self, staged_id: str, commit_message: str | None = None) -> dict:
        staged = self.staged_repo.get(staged_id)
        if not staged:
            raise NotFoundError("staged write not found")
        if staged.status == "committed" and staged.receipt:
            return {"receipt": staged.receipt}
        if staged.expires_at < datetime.utcnow():
            raise ValueError("staged write expired")
        commit_payload = staged.payload.get("commit", {})
        stage_service = StageService(atlas_repo=self.atlas_repo, audit_repo=self.audit_repo)
        commit_service = CommitService(
            atlas_repo=self.atlas_repo,
            graph_repo=self.graph_repo,
            vector_repo=self.vector_repo,
            audit_repo=self.audit_repo,
            notion_repo=self.notion_repo,
        )
        node = stage_service.stage(
            idempotency_key=commit_payload["idempotency_key"],
            title=commit_payload["title"],
            principle=commit_payload["principle"],
            evidence=commit_payload.get("evidence"),
            confidence=commit_payload["confidence"],
            last_verified=_parse_date(commit_payload["last_verified"]),
            links=[AtlasLink(link_type=l["type"], link_value=l["value"]) for l in commit_payload.get("links", [])],
        )
        node = commit_service.commit(idempotency_key=commit_payload["idempotency_key"])
        audit_log_id = self.audit_repo.latest_commit_audit_id(commit_payload["idempotency_key"])
        receipt = {
            "node_id": node.id,
            "principle": node.principle,
            "domain": staged.payload.get("meta", {}).get("domain"),
            "subsystem": staged.payload.get("meta", {}).get("subsystem"),
            "committed_at": datetime.utcnow().isoformat(),
            "audit_log_id": audit_log_id,
            "qdrant_upserted": True,
            "neo4j_updated": True,
            "notion_mirrored": bool(self.notion_repo),
            "links": {
                "api_url": f"{settings.atlas_api_base_url}/atlas/nodes/{node.id}",
                "notion_url": None,
            },
            "commit_message": commit_message,
        }
        self.staged_repo.mark_committed(staged_id=staged_id, node_id=node.id, receipt=receipt)
        return {"receipt": receipt}

    def get_node(self, node_id: str) -> dict:
        node = self.atlas_repo.get_by_id(node_id)
        if not node or node.status != "committed":
            raise NotFoundError("node not found")
        links = self.atlas_repo.get_links(node_id)
        return {
            "node": {
                "id": node.id,
                "title": node.title,
                "principle": node.principle,
                "evidence": node.evidence,
                "confidence": node.confidence,
                "last_verified": str(node.last_verified),
                "links": [{"type": l.link_type, "value": l.link_value} for l in links],
            }
        }


def build_tooling() -> AtlasMcpTooling:
    from app.adapters.postgres.repo import PostgresAtlasRepository, PostgresAuditRepository
    from app.adapters.postgres.staged_repo import StagedWriteRepository
    from app.adapters.qdrant.repo import QdrantVectorRepository
    from app.adapters.neo4j.repo import Neo4jGraphRepository
    from app.adapters.notion.client import NotionMirrorRepository
    from app.embeddings.local_stub import LocalStubEmbeddingProvider

    embedding_provider = LocalStubEmbeddingProvider()
    return AtlasMcpTooling(
        atlas_repo=PostgresAtlasRepository(),
        audit_repo=PostgresAuditRepository(),
        staged_repo=StagedWriteRepository(),
        vector_repo=QdrantVectorRepository(embedding_provider),
        graph_repo=Neo4jGraphRepository(),
        notion_repo=NotionMirrorRepository() if settings.notion_enabled else None,
    )
