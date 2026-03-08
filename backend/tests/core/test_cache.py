"""缓存功能测试."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.cache import SearchCache, LLMCache, generate_cache_key


@pytest.mark.unit
class TestCache:
    """缓存测试."""

    def test_generate_cache_key(self) -> None:
        """测试缓存键生成."""
        key1 = generate_cache_key("search", "query1", {"param": "value"})
        key2 = generate_cache_key("search", "query1", {"param": "value"})
        key3 = generate_cache_key("search", "query2", {"param": "value"})

        assert key1 == key2  # 相同参数生成相同键
        assert key1 != key3  # 不同参数生成不同键
        assert key1.startswith("search:")

    @pytest.mark.asyncio
    async def test_search_cache_key_generation(self) -> None:
        """测试搜索缓存键生成."""
        key1 = SearchCache.generate_key("test query", max_results=10)
        key2 = SearchCache.generate_key("test query", max_results=10)
        key3 = SearchCache.generate_key("different query", max_results=10)

        assert key1 == key2
        assert key1 != key3

    @pytest.mark.asyncio
    async def test_search_cache_key_with_sorted_params(self) -> None:
        """测试搜索缓存键参数排序."""
        # 不同顺序的参数应该生成相同的键
        key1 = SearchCache.generate_key("query", a=1, b=2)
        key2 = SearchCache.generate_key("query", b=2, a=1)

        assert key1 == key2

    @pytest.mark.asyncio
    async def test_llm_cache_key_generation(self) -> None:
        """测试 LLM 缓存键生成."""
        key1 = LLMCache.generate_key("prompt", "gpt-4")
        key2 = LLMCache.generate_key("prompt", "gpt-4")
        key3 = LLMCache.generate_key("different prompt", "gpt-4")

        # 相同输入应该生成相同的哈希
        assert key1 == key2
        assert key1 != key3
        assert key1.startswith("llm:")

    @pytest.mark.asyncio
    async def test_llm_cache_with_extra_params(self) -> None:
        """测试 LLM 缓存键包含额外参数."""
        key1 = LLMCache.generate_key("prompt", "gpt-4", temperature=0.5)
        key2 = LLMCache.generate_key("prompt", "gpt-4", temperature=0.5)
        key3 = LLMCache.generate_key("prompt", "gpt-4", temperature=1.0)

        assert key1 == key2
        assert key1 != key3

    @pytest.mark.asyncio
    @patch("app.core.cache.cache_get")
    async def test_search_cache_get_miss(self, mock_get: AsyncMock) -> None:
        """测试搜索缓存未命中."""
        mock_get.return_value = None

        result = await SearchCache.get("nonexistent query")
        assert result is None

    @pytest.mark.asyncio
    @patch("app.core.cache.cache_set")
    async def test_search_cache_set(self, mock_set: AsyncMock) -> None:
        """测试设置搜索缓存."""
        mock_set.return_value = True
        results = [{"title": "Test", "url": "http://test.com"}]

        await SearchCache.set("test query", results, ttl=300)
        mock_set.assert_called_once()


@pytest.mark.unit
class TestRateLimiter:
    """速率限制器测试."""

    @pytest.mark.asyncio
    async def test_rate_limit_key_generation(self) -> None:
        """测试速率限制键生成."""
        from app.core.rate_limiter import RateLimiter

        key1 = RateLimiter._generate_key("test", "user1")
        key2 = RateLimiter._generate_key("test", "user1")
        key3 = RateLimiter._generate_key("test", "user2")

        assert key1 == key2
        assert key1 != key3

    @pytest.mark.asyncio
    @patch("app.core.redis.redis_get")
    @patch("app.core.redis.redis_set")
    async def test_check_rate_limit_allowed(
        self, mock_set: AsyncMock, mock_get: AsyncMock
    ) -> None:
        """测试允许的速率限制检查."""
        from app.core.rate_limiter import RateLimiter

        mock_get.return_value = None
        mock_set.return_value = True

        limiter = RateLimiter("test_limiter", max_requests=10, window_seconds=60)
        result = await limiter.check("user1")

        assert result is True

    @pytest.mark.asyncio
    @patch("app.core.redis.redis_get")
    async def test_check_rate_limit_exceeded(
        self, mock_get: AsyncMock
    ) -> None:
        """测试超出速率限制."""
        from app.core.rate_limiter import RateLimiter

        mock_get.return_value = "11"  # 已超过限制

        limiter = RateLimiter("test_limiter", max_requests=10, window_seconds=60)
        result = await limiter.check("user1")

        assert result is False


@pytest.mark.integration
class TestCacheWithRedis:
    """需要 Redis 的缓存测试."""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires Redis")
    async def test_cache_set_and_get(self) -> None:
        """测试缓存设置和获取."""
        from app.core.redis import cache_get, cache_set

        await cache_set("test_key", {"data": "value"}, ttl=60)
        result = await cache_get("test_key")

        assert result == {"data": "value"}

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires Redis")
    async def test_cache_delete(self) -> None:
        """测试缓存删除."""
        from app.core.redis import cache_get, cache_set, cache_delete

        await cache_set("delete_key", {"data": "test"}, ttl=60)
        await cache_delete("delete_key")
        result = await cache_get("delete_key")

        assert result is None
