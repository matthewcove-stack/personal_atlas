from app.adapters.neo4j.repo import Neo4jGraphRepository
from app.adapters.notion.client import NotionMirrorRepository
from app.adapters.postgres.repo import PostgresAtlasRepository, PostgresAuditRepository
from app.adapters.qdrant.repo import QdrantVectorRepository
from app.config import settings
from app.core.services import CommitService, SearchService, StageService
from app.embeddings.local_stub import LocalStubEmbeddingProvider

_atlas_repo = PostgresAtlasRepository()
_audit_repo = PostgresAuditRepository()
_graph_repo = Neo4jGraphRepository()
_embedding_provider = LocalStubEmbeddingProvider()
_vector_repo = QdrantVectorRepository(_embedding_provider)
_notion_repo = NotionMirrorRepository() if settings.notion_enabled else None


def get_stage_service() -> StageService:
    return StageService(atlas_repo=_atlas_repo, audit_repo=_audit_repo)


def get_commit_service() -> CommitService:
    return CommitService(
        atlas_repo=_atlas_repo,
        graph_repo=_graph_repo,
        vector_repo=_vector_repo,
        audit_repo=_audit_repo,
        notion_repo=_notion_repo,
    )


def get_search_service() -> SearchService:
    return SearchService(vector_repo=_vector_repo)


def get_atlas_repo() -> PostgresAtlasRepository:
    return _atlas_repo
