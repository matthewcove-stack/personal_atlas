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

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
