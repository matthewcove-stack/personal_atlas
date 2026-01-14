from types import SimpleNamespace

from app.mcp_server.schemas import AtlasNodeInput
from app.mcp_server.tooling import AtlasMcpTooling


class FakeStagedRepo:
    def __init__(self) -> None:
        self.created_payload = None
        self.created_validation = None

    def get_by_idempotency_key(self, idempotency_key: str):
        return None

    def create(self, payload: dict, validation_summary: dict, idempotency_key: str):
        self.created_payload = payload
        self.created_validation = validation_summary
        return SimpleNamespace(
            id="staged-1",
            payload=payload,
            validation_summary=validation_summary,
            idempotency_key=idempotency_key,
        )


class DummyRepo:
    pass


def test_stage_dry_run_matches_stored_payload() -> None:
    staged_repo = FakeStagedRepo()
    tooling = AtlasMcpTooling(
        atlas_repo=DummyRepo(),
        audit_repo=DummyRepo(),
        staged_repo=staged_repo,
        vector_repo=DummyRepo(),
        graph_repo=DummyRepo(),
        notion_repo=None,
    )
    node = AtlasNodeInput(
        domain="Woodworking",
        subsystem="Materials",
        principle="Seal MDF edges before paint.",
        full_knowledge="Seal edges to avoid fuzzing.",
        evidence="Shop tests show smoother finish.",
        tools_materials="MDF, shellac",
        confidence=4,
        last_verified="2025-01-01",
        idempotency_key="k-1",
    )
    response = tooling.stage_node(node)
    assert response["dry_run_payload"] == staged_repo.created_payload["commit"]
