"""Redis 连接管理和工具函数."""

import asyncio
import hashlib
import json
from typing import Any

import redis.asyncio as redis

from app.config import settings

# Redis 连接池
_redis_pool: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    """获取 Redis 连接（单例模式）."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True,
        )
    return _redis_pool


async def close_redis() -> None:
    """关闭 Redis 连接."""
    global _redis_pool
    if _redis_pool:
        await _redis_pool.close()
        _redis_pool = None


# ========== Pub/Sub 功能 ==========

async def publish_message(channel: str, message: dict[str, Any]) -> None:
    """发布消息到指定频道."""
    r = await get_redis()
    await r.publish(channel, json.dumps(message))


async def subscribe_channel(channel: str):
    """订阅指定频道，返回 pubsub 对象."""
    r = await get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(channel)
    return pubsub


# ========== 缓存功能 ==========

async def cache_get(key: str) -> Any:
    """获取缓存."""
    r = await get_redis()
    value = await r.get(key)
    if value:
        return json.loads(value)
    return None


async def cache_set(key: str, value: Any, ttl: int | None = None) -> None:
    """设置缓存（默认使用配置的 TTL）."""
    r = await get_redis()
    ttl = ttl or settings.CACHE_TTL
    await r.setex(key, ttl, json.dumps(value))


async def cache_delete(key: str) -> None:
    """删除缓存."""
    r = await get_redis()
    await r.delete(key)


def generate_cache_key(prefix: str, *args) -> str:
    """生成缓存键."""
    content = ":".join(str(arg) for arg in args)
    hash_value = hashlib.md5(content.encode()).hexdigest()
    return f"{prefix}:{hash_value}"


# ========== 分布式锁 ==========

async def acquire_lock(
    lock_name: str,
    timeout: int = 10,
    retry_times: int = 3,
    retry_delay: float = 0.2,
) -> bool:
    """
    获取分布式锁.

    Args:
        lock_name: 锁名称
        timeout: 锁超时时间（秒）
        retry_times: 重试次数
        retry_delay: 重试延迟（秒）

    Returns:
        是否成功获取锁
    """
    r = await get_redis()
    lock_key = f"lock:{lock_name}"

    for _ in range(retry_times):
        # 尝试设置锁
        acquired = await r.set(lock_key, "1", nx=True, ex=timeout)
        if acquired:
            return True
        # 等待后重试
        await asyncio.sleep(retry_delay)

    return False


async def release_lock(lock_name: str) -> None:
    """释放分布式锁."""
    r = await get_redis()
    lock_key = f"lock:{lock_name}"
    await r.delete(lock_key)
