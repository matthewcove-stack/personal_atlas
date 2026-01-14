import uuid

import pytest
psycopg2 = pytest.importorskip("psycopg2")
from neo4j import GraphDatabase
from qdrant_client import QdrantClient

from app.config import settings
from app.mcp_server.schemas import AtlasNodeInput
from app.mcp_server.tooling import build_tooling


def _services_available() -> bool:
    try:
        psycopg2.connect(
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
            host=settings.postgres_host,
            port=settings.postgres_port,
        ).close()
    except Exception:
        return False
    try:
        client = QdrantClient(url=settings.qdrant_url)
        client.get_collections()
    except Exception:
        return False
    try:
        driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        with driver.session() as session:
            session.run("RETURN 1")
    except Exception:
        return False
    return True


@pytest.mark.skipif(not _services_available(), reason="Graph/vector services not available")
def test_mcp_stage_commit_search_idempotent() -> None:
    tooling = build_tooling()
    key = f"mcp-{uuid.uuid4()}"
    node = AtlasNodeInput(
        domain="Woodworking",
        subsystem="Materials",
        principle="Seal MDF edges before paint.",
        full_knowledge="Seal edges to avoid fuzzing.",
        evidence="Shop tests show smoother finish.",
        tools_materials="MDF, shellac",
        confidence=4,
        last_verified="2025-01-01",
        idempotency_key=key,
    )
    staged = tooling.stage_node(node)
    receipt = tooling.commit_node(staged_id=staged["staged_id"])["receipt"]
    search = tooling.search(query="MDF", top_k=3)
    assert any(r["id"] == receipt["node_id"] for r in search["results"])

    receipt_again = tooling.commit_node(staged_id=staged["staged_id"])["receipt"]
    assert receipt_again["node_id"] == receipt["node_id"]
    assert tooling.audit_repo.commit_count(key) == 1
