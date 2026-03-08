"""用户环境配置 API 端点."""

import os
from typing import Dict

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUserDep, DBDep
from app.models.user_env_config import UserEnvConfig
from app.schemas.user_env_config import (
    UserEnvConfigCreate,
    UserEnvConfigInitResponse,
    UserEnvConfigResponse,
    UserEnvConfigUpdate,
)

router = APIRouter(prefix="/user-env-config", tags=["user-env-config"])

# 从 .env 文件读取的环境变量默认值
DEFAULT_ENV_VARS: Dict[str, str] = {}

# 硬编码的默认环境变量（当 .env 文件不可用时使用）
HARDCODED_DEFAULTS: Dict[str, str] = {
    # 数据库配置
    "MYSQL_ROOT_PASSWORD": "deepresearch",
    "MYSQL_USER": "drw",
    "MYSQL_PASSWORD": "drw_pass",
    "DATABASE_URL": "mysql+pymysql://drw:drw_pass@mysql:3306/deepresearch",
    "DB_POOL_SIZE": "20",
    "DB_MAX_OVERFLOW": "30",
    "DB_POOL_RECYCLE": "3600",
    # Neo4j 配置
    "NEO4J_URI": "bolt://neo4j:7687",
    "NEO4J_USER": "neo4j",
    "NEO4J_PASSWORD": "deepresearch",
    "NEO4J_MAX_CONNECTIONS": "50",
    # Redis 配置
    "REDIS_URL": "redis://redis:6379/0",
    "REDIS_MAX_CONNECTIONS": "100",
    "CACHE_TTL": "1800",
    # RabbitMQ 配置
    "RABBITMQ_URL": "amqp://guest:guest@rabbitmq:5672/",
    "RABBITMQ_USER": "guest",
    "RABBITMQ_PASSWORD": "guest",
    # Milvus 配置
    "MILVUS_HOST": "milvus-standalone",
    "MILVUS_PORT": "19530",
    "MILVUS_USER": "root",
    "MILVUS_PASSWORD": "milvus",
    "MILVUS_MAX_CONNECTIONS": "30",
    # Qdrant 配置
    "QDRANT_HOST": "qdrant",
    "QDRANT_PORT": "6333",
    "QDRANT_GRPC_PORT": "6334",
    # JWT 配置
    "SECRET_KEY": "your-super-secret-key-change-in-production-min-32-chars",
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    # LLM 配置
    "OPENAI_API_KEY": "",
    "LLM_BASE_URL": "https://api.minimaxi.com/v1",
    "LLM_MODEL": "MiniMax-M2.5",
    "LLM_MAX_CONCURRENT": "20",
    # 搜索配置
    "TAVILY_API_KEY": "",
    "SERPAPI_KEY": "",
    # ARQ 配置
    "ARQ_MAX_JOBS": "50",
    "ARQ_JOB_TIMEOUT": "600",
    "ARQ_MAX_TRIES": "3",
    "ARQ_HEALTH_CHECK_INTERVAL": "30",
    # MemOS 配置
    "USE_MEMOS": "false",
    "MEMOS_EXPLICIT_PREF_COLLECTION": "explicit_preference",
    "MEMOS_IMPLICIT_PREF_COLLECTION": "implicit_preference",
    "MEMOS_TREE_COLLECTION": "tree_memory",
    "MEMOS_EMBEDDING_MODEL": "BAAI/bge-large-zh-v1.5",
    "MEMOS_EMBEDDING_URL": "https://api.openai.com/v1/embeddings",
    "MEMOS_EMBEDDING_API_KEY": "",
    "MEMOS_RERANKER_MODEL": "BAAI/bge-reranker-base",
    "MEMOS_RERANKER_URL": "",
    "MEMOS_RERANKER_API_KEY": "",
    # 应用配置
    "DEBUG": "false",
    "ENV": "production",
    "APP_NAME": "DeepResearchWeb",
    "APP_VERSION": "0.1.0",
    "CORS_ORIGINS": "http://localhost:3000,http://localhost:5173",
}


def load_default_env_vars() -> Dict[str, str]:
    """从 .env 文件加载默认环境变量，如果失败则使用硬编码默认值."""
    global DEFAULT_ENV_VARS

    if DEFAULT_ENV_VARS:
        return DEFAULT_ENV_VARS

    # 尝试从多个位置加载 .env 文件
    env_paths = [
        "/app/.env",
        "/Users/xiniuyiliao/Desktop/code/DeepResearchWeb/.env",
        ".env",
        "../.env",
    ]

    loaded = False
    for env_path in env_paths:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        # 跳过注释和空行
                        if not line or line.startswith("#"):
                            continue
                        # 解析 KEY=VALUE 格式
                        if "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip()
                            # 移除引号
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            DEFAULT_ENV_VARS[key] = value
                loaded = True
                break
            except Exception:
                continue

    # 如果没有加载成功，使用硬编码默认值
    if not loaded:
        DEFAULT_ENV_VARS = HARDCODED_DEFAULTS.copy()

    return DEFAULT_ENV_VARS


@router.get(
    "",
    response_model=UserEnvConfigInitResponse,
    summary="获取用户环境配置",
)
async def get_user_env_config(
    db: DBDep,
    current_user: CurrentUserDep,
    config_name: str = "default",
) -> UserEnvConfigInitResponse:
    """
    获取用户的环境配置.

    - 如果用户没有配置，返回 .env 文件中的默认值
    - 如果用户已有配置，返回用户的自定义配置
    """
    # 查找用户的配置
    result = await db.execute(
        select(UserEnvConfig).where(
            UserEnvConfig.user_id == current_user.id,
            UserEnvConfig.config_name == config_name,
        )
    )
    user_config = result.scalar_one_or_none()

    if user_config:
        return UserEnvConfigInitResponse(
            env_config=user_config.env_config,
            is_new=False,
        )

    # 返回默认配置
    default_config = load_default_env_vars()
    return UserEnvConfigInitResponse(
        env_config=default_config,
        is_new=True,
    )


@router.post(
    "",
    response_model=UserEnvConfigResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户环境配置",
)
async def create_user_env_config(
    db: DBDep,
    current_user: CurrentUserDep,
    data: UserEnvConfigCreate,
) -> UserEnvConfigResponse:
    """创建用户的环境配置（首次保存时使用）."""
    # 检查是否已存在
    result = await db.execute(
        select(UserEnvConfig).where(
            UserEnvConfig.user_id == current_user.id,
            UserEnvConfig.config_name == data.config_name,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Configuration already exists, use PUT to update",
        )

    # 创建新配置
    config = UserEnvConfig(
        user_id=current_user.id,
        config_name=data.config_name,
        env_config=data.env_config,
    )
    db.add(config)

    try:
        await db.commit()
        await db.refresh(config)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Configuration already exists",
        )

    return config


@router.put(
    "",
    response_model=UserEnvConfigResponse,
    summary="更新用户环境配置",
)
async def update_user_env_config(
    db: DBDep,
    current_user: CurrentUserDep,
    data: UserEnvConfigUpdate,
    config_name: str = "default",
) -> UserEnvConfigResponse:
    """更新用户的环境配置."""
    # 查找现有配置
    result = await db.execute(
        select(UserEnvConfig).where(
            UserEnvConfig.user_id == current_user.id,
            UserEnvConfig.config_name == config_name,
        )
    )
    config = result.scalar_one_or_none()

    if config:
        # 更新现有配置
        config.env_config = data.env_config
    else:
        # 创建新配置
        config = UserEnvConfig(
            user_id=current_user.id,
            config_name=config_name,
            env_config=data.env_config,
        )
        db.add(config)

    await db.commit()
    await db.refresh(config)

    return config


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除用户环境配置",
)
async def delete_user_env_config(
    db: DBDep,
    current_user: CurrentUserDep,
    config_name: str = "default",
) -> None:
    """删除用户的环境配置."""
    result = await db.execute(
        select(UserEnvConfig).where(
            UserEnvConfig.user_id == current_user.id,
            UserEnvConfig.config_name == config_name,
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found",
        )

    await db.delete(config)
    await db.commit()
