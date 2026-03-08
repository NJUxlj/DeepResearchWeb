"""Pytest 配置和 Fixtures."""

import asyncio
from typing import Any, AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.db.database import Base, get_db
from app.main import create_app


# 测试数据库 URL
TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    "deepresearch", "deepresearch_test"
) if "deepresearch" in settings.DATABASE_URL else "sqlite+aiosqlite:///:memory:"

# 创建测试引擎
engine = create_async_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)

# 测试会话工厂
TestingSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建事件循环."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def setup_database() -> AsyncGenerator[None, None]:
    """设置测试数据库."""
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    # 清理
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(setup_database: None) -> AsyncGenerator[AsyncSession, None]:
    """创建数据库会话."""
    async with TestingSessionLocal() as session:
        yield session
        # 回滚事务
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """创建测试客户端."""
    app = create_app()

    # 覆盖数据库依赖
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def mock_user_data() -> dict[str, str]:
    """模拟用户数据."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123456",
    }


@pytest.fixture
def mock_settings(mocker: Any) -> None:
    """模拟配置."""
    mocker.patch.object(settings, "SECRET_KEY", "test-secret-key-for-testing")
    mocker.patch.object(settings, "OPENAI_API_KEY", "test-openai-key")
    mocker.patch.object(settings, "TAVILY_API_KEY", "test-tavily-key")
    mocker.patch.object(settings, "LLM_BASE_URL", "https://api.openai.com/v1")
    mocker.patch.object(settings, "DEBUG", True)


@pytest.fixture
def mock_redis(mocker: Any) -> MagicMock:
    """模拟 Redis."""
    mock = MagicMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=1)
    return mock


@pytest.fixture
def mock_openai_client(mocker: Any) -> MagicMock:
    """模拟 OpenAI 客户端."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"needs_clarification": false, "clarification_question": null, "sub_queries": [{"id": "1", "query": "test query", "strategy": "web_search", "target": null, "priority": 5}]}'))
    ]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    return mock_client
