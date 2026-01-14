from datetime import date, datetime

from app.core.domain import AtlasLink, AtlasNode
from app.core.services import StageService


class FakeAtlasRepo:
    def __init__(self) -> None:
        self.nodes = {}

    def get_by_idempotency_key(self, idempotency_key: str):
        return self.nodes.get(idempotency_key)

    def create_staged_node(
        self,
        idempotency_key: str,
        title: str,
        principle: str,
        evidence: str | None,
        confidence: int,
        last_verified: date,
        links: list[AtlasLink],
    ) -> AtlasNode:
        node = AtlasNode(
            id="node-1",
            title=title,
            principle=principle,
            evidence=evidence,
            confidence=confidence,
            last_verified=last_verified,
            status="staged",
            idempotency_key=idempotency_key,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.nodes[idempotency_key] = node
        return node

    def mark_committed(self, node_id: str):
        raise NotImplementedError

    def get_by_id(self, node_id: str):
        raise NotImplementedError

    def get_links(self, node_id: str):
        return []


class FakeAuditRepo:
    def __init__(self) -> None:
        self.logs = []

    def log(
        self,
        action: str,
        entity_type: str,
        entity_id: str | None,
        idempotency_key: str,
        status: str,
        message: str | None = None,
    ) -> None:
        self.logs.append((action, status))


def test_stage_idempotency_returns_existing_node() -> None:
    atlas_repo = FakeAtlasRepo()
    audit_repo = FakeAuditRepo()
    service = StageService(atlas_repo=atlas_repo, audit_repo=audit_repo)

    first = service.stage(
        idempotency_key="k1",
        title="title",
        principle="principle",
        evidence=None,
        confidence=3,
        last_verified=date(2025, 1, 1),
        links=[],
    )
    second = service.stage(
        idempotency_key="k1",
        title="title",
        principle="principle",
        evidence=None,
        confidence=3,
        last_verified=date(2025, 1, 1),
        links=[],
    )
    assert first.id == second.id
