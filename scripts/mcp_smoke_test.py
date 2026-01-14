import uuid

from app.mcp_server.schemas import AtlasNodeInput
from app.mcp_server.tooling import build_tooling


def main() -> None:
    tooling = build_tooling()
    key = f"smoke-{uuid.uuid4()}"
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
    print("receipt:", receipt)
    print("search results:", search["results"])


if __name__ == "__main__":
    main()
