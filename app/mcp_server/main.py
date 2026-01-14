from mcp.server.fastmcp import FastMCP

from app.config import settings
from app.mcp_server.schemas import AtlasNodeInput
from app.mcp_server.tooling import build_tooling

mcp = FastMCP("personal_atlas")
tooling = build_tooling()


@mcp.tool()
def atlas_health() -> dict:
    return tooling.health()


@mcp.tool()
def atlas_search(query: str, top_k: int = 5, domain: str | None = None, subsystem: str | None = None) -> dict:
    return tooling.search(query=query, top_k=top_k, domain=domain, subsystem=subsystem)


@mcp.tool()
def atlas_stage_node(node: AtlasNodeInput) -> dict:
    return tooling.stage_node(node)


@mcp.tool()
def atlas_commit_node(staged_id: str, commit_message: str | None = None) -> dict:
    return tooling.commit_node(staged_id=staged_id, commit_message=commit_message)


@mcp.tool()
def atlas_get_node(node_id: str) -> dict:
    return tooling.get_node(node_id)


if __name__ == "__main__":
    mcp.run(host=settings.mcp_host, port=settings.mcp_port)
