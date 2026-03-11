"""FastAPI 应用入口."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import auth, chat, health, memory, messages, research, sessions, tools, skills, mcp, user_env_config, user_settings
from app.config import settings
from app.core.exceptions import setup_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import setup_middleware
from app.core.redis import close_redis, get_redis
from app.db.database import close_db, init_db

# 初始化日志
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理."""
    # 启动时初始化
    await init_db()

    # 初始化 Redis 连接（确保连接池预热）
    try:
        await get_redis()
    except Exception as e:
        print(f"Warning: Redis connection failed: {e}")

    yield

    # 关闭时清理
    await close_redis()
    await close_db()


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # 配置中间件
    setup_middleware(app)

    # 配置异常处理
    setup_exception_handlers(app)

    # 注册路由
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(sessions.router, prefix="/api/v1")
    app.include_router(messages.router, prefix="/api/v1")
    app.include_router(chat.router, prefix="/api/v1")
    app.include_router(research.router, prefix="/api/v1")
    app.include_router(memory.router, prefix="/api/v1")
    app.include_router(tools.router, prefix="/api/v1")
    app.include_router(skills.router, prefix="/api/v1")
    app.include_router(mcp.router, prefix="/api/v1")
    app.include_router(user_env_config.router, prefix="/api/v1")
    app.include_router(user_settings.router, prefix="/api/v1")

    return app


app = create_app()


@app.get("/")
async def root():
    """根路径重定向到文档."""
    return {
        "message": "Welcome to DeepResearchWeb API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
