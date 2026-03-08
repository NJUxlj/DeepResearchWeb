"""搜索结果缓存管理."""

import hashlib
from typing import Any, Callable, TypeVar

from app.core.redis import cache_get, cache_set, generate_cache_key
from app.config import settings

T = TypeVar("T")


class SearchCache:
    """搜索缓存管理器."""

    DEFAULT_TTL = 1800  # 30 分钟

    @staticmethod
    def generate_key(query: str, **kwargs) -> str:
        """生成搜索缓存键."""
        # 排序 kwargs 确保一致性
        params = f"{query}:{sorted(kwargs.items())}"
        return generate_cache_key("search", params)

    @staticmethod
    async def get(query: str, **kwargs) -> Any:
        """获取缓存的搜索结果."""
        key = SearchCache.generate_key(query, **kwargs)
        return await cache_get(key)

    @staticmethod
    async def set(query: str, results: Any, ttl: int = DEFAULT_TTL, **kwargs) -> None:
        """缓存搜索结果."""
        key = SearchCache.generate_key(query, **kwargs)
        await cache_set(key, results, ttl)


async def cached_search(
    search_func: Callable[..., T],
    query: str,
    **kwargs: Any,
) -> T:
    """
    带缓存的搜索装饰器（作为独立函数使用）.

    Usage:
        results = await cached_search(tavily_search, "query", max_results=5)
    """
    # 尝试从缓存获取
    cached = await SearchCache.get(query, **kwargs)
    if cached is not None:
        return cached

    # 执行搜索
    results = await search_func(query, **kwargs)

    # 缓存结果
    await SearchCache.set(query, results, **kwargs)

    return results


class LLMCache:
    """LLM 响应缓存管理器."""

    DEFAULT_TTL = 3600  # 1 小时

    @staticmethod
    def generate_key(prompt: str, model: str, **kwargs) -> str:
        """生成 LLM 缓存键."""
        content = f"{prompt}:{model}:{sorted(kwargs.items())}"
        hash_value = hashlib.sha256(content.encode()).hexdigest()
        return f"llm:{hash_value[:16]}"

    @staticmethod
    async def get(prompt: str, model: str, **kwargs) -> Any:
        """获取缓存的 LLM 响应."""
        key = LLMCache.generate_key(prompt, model, **kwargs)
        return await cache_get(key)

    @staticmethod
    async def set(prompt: str, response: Any, ttl: int = DEFAULT_TTL, **kwargs) -> None:
        """缓存 LLM 响应."""
        key = LLMCache.generate_key(prompt, model=kwargs.get("model", "default"), **kwargs)
        await cache_set(key, response, ttl)
