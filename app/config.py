from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int

    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str

    qdrant_url: str

    notion_enabled: bool = False
    notion_token: str | None = None
    notion_database_id: str | None = None

    embedding_dim: int = 8
    staged_write_ttl_minutes: int = 1440
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8765
    atlas_api_base_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
