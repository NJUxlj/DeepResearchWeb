"""LLM 并发控制和速率限制."""

import asyncio
from typing import Any, Callable, TypeVar

from app.config import settings
from app.core.redis import cache_get, cache_set, get_redis

T = TypeVar("T")


class LLMRateLimiter:
    """LLM 调用速率限制器."""

    def __init__(self, max_concurrent: int | None = None, rpm_limit: int = 500):
        self._semaphore = asyncio.Semaphore(
            max_concurrent or settings.LLM_MAX_CONCURRENT
        )
        self._rpm_limit = rpm_limit
        self._window_size = 60  # 滑动窗口大小（秒）

    async def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        在信号量控制下执行函数.

        Args:
            func: 要执行的异步函数
            *args, **kwargs: 函数参数

        Returns:
            函数执行结果
        """
        # 检查 RPM 限制
        await self._check_rpm_limit()

        async with self._semaphore:
            return await func(*args, **kwargs)

    async def _check_rpm_limit(self) -> None:
        """检查并等待 RPM 限制."""
        r = await get_redis()
        key = "llm:rpm:count"

        current = await r.get(key)
        if current and int(current) >= self._rpm_limit:
            # 等待窗口重置
            await asyncio.sleep(1)
            await self._check_rpm_limit()
        else:
            # 增加计数
            pipe = r.pipeline()
            pipe.incr(key)
            pipe.expire(key, self._window_size)
            await pipe.execute()


# 全局限流器实例
llm_limiter = LLMRateLimiter()


async def limited_llm_call(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """使用全局限流器调用 LLM."""
    return await llm_limiter.call(func, *args, **kwargs)


class RateLimiter:
    """通用速率限制器（基于滑动窗口）."""

    def __init__(self, key: str, limit: int, window: int = 60):
        """
        初始化速率限制器.

        Args:
            key: Redis 键前缀
            limit: 时间窗口内的最大请求数
            window: 时间窗口大小（秒）
        """
        self.key = f"ratelimit:{key}"
        self.limit = limit
        self.window = window

    async def acquire(self) -> bool:
        """
        尝试获取令牌.

        Returns:
            是否成功获取令牌
        """
        r = await get_redis()

        current = await r.get(self.key)
        if current and int(current) >= self.limit:
            return False

        # 使用 INCR 和 EXPIRE 实现滑动窗口
        pipe = r.pipeline()
        pipe.incr(self.key)
        # 只有首次设置时才设置过期时间
        if not current:
            pipe.expire(self.key, self.window)
        await pipe.execute()

        return True

    async def wait_and_acquire(self) -> None:
        """等待直到获取到令牌."""
        while not await self.acquire():
            await asyncio.sleep(0.1)

    async def get_current_count(self) -> int:
        """获取当前计数."""
        r = await get_redis()
        current = await r.get(self.key)
        return int(current) if current else 0
