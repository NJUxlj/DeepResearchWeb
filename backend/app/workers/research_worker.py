"""ARQ Worker: 异步执行研究任务."""

import asyncio
from datetime import datetime
from typing import Any

import asyncmy
import sqlalchemy
from arq import create_pool
from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.agents.research_agent import ResearchAgent
from app.config import settings
from app.core.redis import publish_message
from app.models.research_task import ResearchTask
from app.schemas.research import ResearchConfig

# ARQ Redis 配置
arq_redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)


def _create_db_engine():
    """创建数据库引擎."""
    return create_async_engine(
        settings.DATABASE_URL.replace("mysql+pymysql", "mysql+aiomysql"),
        pool_size=5,
        max_overflow=10,
    )


async def run_research_task(
    ctx: dict,
    task_id: int,
    query: str,
    user_id: int,
    session_id: int,
    config: dict[str, Any],
) -> dict[str, Any]:
    """
    执行研究任务.

    这是一个 ARQ 任务，在 Worker 进程中异步执行.

    Args:
        ctx: ARQ 上下文
        task_id: 任务 ID
        query: 研究查询
        user_id: 用户 ID
        session_id: 会话 ID
        config: 研究配置

    Returns:
        任务结果
    """
    # 创建数据库连接
    engine = _create_db_engine()
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as db:
            # 更新任务状态为 running
            result = await db.execute(
                sqlalchemy.select(ResearchTask).where(ResearchTask.id == task_id)
            )
            task = result.scalar_one_or_none()

            if task:
                task.status = "running"
                task.started_at = datetime.utcnow()
                await db.commit()

            # 执行研究
            research_config = ResearchConfig(**config) if config else ResearchConfig()
            agent = ResearchAgent(research_config)

            async def on_event(event: str, data: dict) -> None:
                """事件回调，通过 Redis Pub/Sub 推送."""
                await publish_message(
                    f"research:{task_id}",
                    {
                        "event": event,
                        "data": data,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

            # 执行研究任务
            result = await agent.research(query, user_id, on_event)

            # 更新任务完成状态
            if task:
                task.status = "completed"
                task.completed_at = datetime.utcnow()
                task.iterations = len(result.get("iterations", []))
                task.sources_count = result.get("total_sources", 0)
                task.result = {
                    "query": result.get("query"),
                    "final_report": result.get("final_report"),
                    "citations": result.get("citations", []),
                    "total_sources": result.get("total_sources", 0),
                    "completed_at": datetime.utcnow().isoformat(),
                }
                await db.commit()

            # 发送完成消息
            await publish_message(
                f"research:{task_id}",
                {"event": "complete", "data": {"task_id": task_id}},
            )

            return {"status": "completed", "task_id": task_id}

    except Exception as e:
        # 更新失败状态
        engine = _create_db_engine()
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as db:
            result = await db.execute(
                sqlalchemy.select(ResearchTask).where(ResearchTask.id == task_id)
            )
            task = result.scalar_one_or_none()

            if task:
                task.status = "failed"
                task.error = str(e)
                await db.commit()

        # 发送错误消息
        await publish_message(
            f"research:{task_id}",
            {"event": "error", "data": {"error": str(e)}},
        )

        raise

    finally:
        await engine.dispose()


class WorkerSettings:
    """ARQ Worker 配置."""

    redis_settings = arq_redis_settings

    # 任务函数
    functions = [run_research_task]

    # 并发设置
    max_jobs = settings.ARQ_MAX_JOBS
    job_timeout = settings.ARQ_JOB_TIMEOUT

    # 重试设置
    retry_jobs = True
    max_tries = settings.ARQ_MAX_TRIES

    # 健康检查
    health_check_interval = settings.ARQ_HEALTH_CHECK_INTERVAL


async def enqueue_research_task(
    redis_pool,
    task_id: int,
    query: str,
    user_id: int,
    session_id: int,
    config: dict[str, Any],
) -> str:
    """将研究任务加入队列."""
    job = await redis_pool.enqueue_job(
        "run_research_task",
        task_id=task_id,
        query=query,
        user_id=user_id,
        session_id=session_id,
        config=config,
    )
    return job.job_id


async def create_redis_pool() -> Any:
    """创建 ARQ Redis 连接池."""
    return await create_pool(arq_redis_settings)
