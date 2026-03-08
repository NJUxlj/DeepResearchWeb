"""健康检查和监控端点."""

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.config import settings
from app.core.redis import get_redis

router = APIRouter(tags=["health", "monitoring"])


class HealthResponse(BaseModel):
    """健康检查响应."""

    status: str
    version: str
    environment: str


class HealthDetailResponse(BaseModel):
    """详细健康检查响应."""

    status: str
    version: str
    environment: str
    database: str
    redis: str


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="基础健康检查",
)
async def health_check() -> HealthResponse:
    """基础健康检查端点."""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.ENV,
    )


@router.get(
    "/health/detail",
    response_model=HealthDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="详细健康检查",
)
async def health_check_detail(
    db: AsyncSession = Depends(get_db),
) -> HealthDetailResponse:
    """详细健康检查，验证数据库和 Redis 连接."""
    db_status = "disconnected"
    redis_status = "disconnected"

    try:
        # 验证数据库连接
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        pass

    # 验证 Redis 连接
    try:
        redis = await get_redis()
        await redis.ping()
        redis_status = "connected"
    except Exception:
        pass

    is_healthy = db_status == "connected" and redis_status == "connected"

    return HealthDetailResponse(
        status="healthy" if is_healthy else "degraded",
        version=settings.APP_VERSION,
        environment=settings.ENV,
        database=db_status,
        redis=redis_status,
    )


# 保留旧路由以兼容
@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="基础健康检查 (旧)",
)
async def health_check_legacy() -> HealthResponse:
    """基础健康检查端点 (兼容旧版本)."""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        environment=settings.ENV,
    )
