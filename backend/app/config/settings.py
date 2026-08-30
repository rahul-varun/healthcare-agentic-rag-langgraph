from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM
    llm_provider: str = "openrouter"
    llm_model: str = "inclusionai/ling-3.0-flash-fin:free"
    openrouter_api_key: str = ""
    llm_cost_per_1k_input_tokens: float = 0.0
    llm_cost_per_1k_output_tokens: float = 0.0
    llm_max_retries: int = 2
    llm_retry_base_delay_seconds: float = 0.5

    # Embeddings
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # Reranking
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # Vector DB
    vector_db_provider: str = "chroma"
    chroma_persist_dir: str = "./data/chroma"
    qdrant_url: str = "http://localhost:6333"

    # Postgres
    postgres_url: str = "postgresql://postgres:postgres@localhost:5432/agentic_rag"

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    # Web search tool
    tavily_api_key: str = ""
    web_search_max_results: int = 5
    web_search_timeout_seconds: int = 10
    web_search_max_content_chars: int = 2000
    web_search_allowed_domains: str = ""  # comma-separated allowlist; empty = no restriction

    # SQL tool
    sql_max_rows: int = 100
    sql_timeout_seconds: int = 10

    # Observability
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    # App
    environment: str = "development"
    max_agent_iterations: int = 8
    request_timeout_seconds: int = 30
    max_input_chars: int = 4000
    max_upload_size_mb: int = 25

    # Auth / rate limiting / caching (Phase 9)
    api_key: str = ""  # empty disables auth (local dev)
    rate_limit_max_requests: int = 60
    rate_limit_window_seconds: float = 60.0
    cache_ttl_seconds: float = 60.0
    cors_allowed_origins: str = "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
