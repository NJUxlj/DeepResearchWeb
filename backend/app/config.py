"""应用配置管理."""

from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ========== 应用基础配置 ==========
    APP_NAME: str = "DeepResearchWeb"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENV: str = Field(default="development", env="ENV")

    # ========== 数据库配置 ==========
    DATABASE_URL: str = Field(
        default="mysql+pymysql://drw:drw_pass@localhost:3306/deepresearch",
        env="DATABASE_URL",
    )
    DB_POOL_SIZE: int = Field(default=20, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=30, env="DB_MAX_OVERFLOW")
    DB_POOL_RECYCLE: int = Field(default=3600, env="DB_POOL_RECYCLE")

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith("mysql+pymysql://"):
            raise ValueError("DATABASE_URL must use mysql+pymysql:// scheme")
        return v

    # ========== Redis 配置 ==========
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_MAX_CONNECTIONS: int = Field(default=100, env="REDIS_MAX_CONNECTIONS")

    # ========== Neo4j 配置 ==========
    NEO4J_URI: str = Field(default="bolt://localhost:7687", env="NEO4J_URI")
    NEO4J_USER: str = Field(default="neo4j", env="NEO4J_USER")
    NEO4J_PASSWORD: str = Field(default="deepresearch", env="NEO4J_PASSWORD")
    NEO4J_MAX_CONNECTIONS: int = Field(default=50, env="NEO4J_MAX_CONNECTIONS")

    # ========== Milvus 配置 ==========
    MILVUS_HOST: str = Field(default="localhost", env="MILVUS_HOST")
    MILVUS_PORT: int = Field(default=19530, env="MILVUS_PORT")
    MILVUS_USER: str = Field(default="root", env="MILVUS_USER")
    MILVUS_PASSWORD: str = Field(default="milvus", env="MILVUS_PASSWORD")
    MILVUS_MAX_CONNECTIONS: int = Field(default=30, env="MILVUS_MAX_CONNECTIONS")

    # ========== Qdrant 配置 ==========
    QDRANT_HOST: str = Field(default="localhost", env="QDRANT_HOST")
    QDRANT_PORT: int = Field(default=6333, env="QDRANT_PORT")
    QDRANT_GRPC_PORT: int = Field(default=6334, env="QDRANT_GRPC_PORT")

    # ========== RabbitMQ 配置 ==========
    RABBITMQ_URL: str = Field(
        default="amqp://guest:guest@localhost:5672/", env="RABBITMQ_URL"
    )

    # ========== JWT 配置 ==========
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # ========== LLM 配置 ==========
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    LLM_BASE_URL: Optional[str] = Field(default=None, env="LLM_BASE_URL")
    LLM_MODEL: str = Field(default="gpt-4o-mini", env="LLM_MODEL")
    LLM_MAX_CONCURRENT: int = Field(default=20, env="LLM_MAX_CONCURRENT")

    # ========== 搜索配置 ==========
    TAVILY_API_KEY: Optional[str] = Field(default=None, env="TAVILY_API_KEY")
    SERPAPI_KEY: Optional[str] = Field(default=None, env="SERPAPI_KEY")

    # ========== CORS 配置 ==========
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:5173", env="CORS_ORIGINS")

    # ========== MemOS 配置 ==========
    
    # 偏好记忆集合配置（Milvus 向量存储）
    MEMOS_EXPLICIT_PREF_COLLECTION: str = Field(default="explicit_preference", env="MEMOS_EXPLICIT_PREF_COLLECTION")
    MEMOS_IMPLICIT_PREF_COLLECTION: str = Field(default="implicit_preference", env="MEMOS_IMPLICIT_PREF_COLLECTION")
    
    # 树形记忆集合配置（Qdrant 向量存储 + Neo4j 图存储）
    MEMOS_TREE_COLLECTION: str = Field(default="tree_memory", env="MEMOS_TREE_COLLECTION")
    
    # Embedding 模型配置（用于偏好记忆和树形记忆的向量化）
    MEMOS_EMBEDDING_MODEL: str = Field(default="BAAI/bge-large-zh-v1.5", env="MEMOS_EMBEDDING_MODEL")
    MEMOS_EMBEDDING_URL: str | None = Field(default=None, env="MEMOS_EMBEDDING_URL")
    MEMOS_EMBEDDING_API_KEY: str | None = Field(default=None, env="MEMOS_EMBEDDING_API_KEY")
    
    # Reranker 模型配置（用于搜索结果重排序）
    MEMOS_RERANKER_MODEL: str = Field(default="BAAI/bge-reranker-base", env="MEMOS_RERANKER_MODEL")
    MEMOS_RERANKER_URL: str | None = Field(default=None, env="MEMOS_RERANKER_URL")
    MEMOS_RERANKER_API_KEY: str | None = Field(default=None, env="MEMOS_RERANKER_API_KEY")
    
    # MemOS 开关
    USE_MEMOS: bool = Field(default=False, env="USE_MEMOS")

    # ========== ARQ 任务队列配置 ==========
    ARQ_MAX_JOBS: int = Field(default=50, env="ARQ_MAX_JOBS")
    ARQ_JOB_TIMEOUT: int = Field(default=600, env="ARQ_JOB_TIMEOUT")
    ARQ_MAX_TRIES: int = Field(default=3, env="ARQ_MAX_TRIES")
    ARQ_HEALTH_CHECK_INTERVAL: int = Field(default=30, env="ARQ_HEALTH_CHECK_INTERVAL")

    # ========== 缓存配置 ==========
    CACHE_TTL: int = Field(default=1800, env="CACHE_TTL")  # 30 分钟


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例."""
    return Settings()


settings = get_settings()
