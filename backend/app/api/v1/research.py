"""Research API 端点 (ARQ 集成版本)."""

import json
from datetime import datetime

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.agents.research_agent import ResearchAgent
from app.api.deps import CurrentUserDep, DBDep
from app.config import settings
from app.core.redis import get_redis, subscribe_channel
from app.models.research_task import ResearchTask
from app.models.session import Session
from app.schemas.research import (
    ResearchConfig,
    ResearchRequest,
    ResearchTaskDetail,
    ResearchTaskResponse,
)
from app.workers.research_worker import arq_redis_settings, enqueue_research_task

router = APIRouter(prefix="/research", tags=["research"])


@router.post("/tasks")
async def create_research_task(
    db: DBDep,
    current_user: CurrentUserDep,
    request: ResearchRequest,
):
    """
    创建研究任务并加入 ARQ 队列.

    Args:
        db: 数据库会话
        current_user: 当前用户
        request: 研究请求

    Returns:
        任务信息
    """
    if not request.query:
        raise HTTPException(status_code=422, detail="Query is required")

    # 获取或创建会话
    if request.session_id:
        result = await db.execute(
            select(Session).where(
                Session.id == request.session_id,
                Session.user_id == current_user.id,
            )
        )
        session = result.scalar_one_or_none()
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = Session(
            user_id=current_user.id,
            title=request.query[:50] + "..." if len(request.query) > 50 else request.query,
            mode="research",
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

    # 创建任务记录
    config_dict = request.config.model_dump() if request.config else {}
    task = ResearchTask(
        session_id=session.id,
        user_id=current_user.id,
        query=request.query,
        config=config_dict,
        status="pending",
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    # 加入 ARQ 队列
    redis_pool = await create_pool(arq_redis_settings)
    job_id = await enqueue_research_task(
        redis_pool,
        task_id=task.id,
        query=request.query,
        user_id=current_user.id,
        session_id=session.id,
        config=config_dict,
    )

    return {
        "task_id": task.id,
        "job_id": job_id,
        "status": "pending",
        "session_id": session.id,
    }


@router.get("/tasks/{task_id}/stream")
async def research_task_stream(
    db: DBDep,
    current_user: CurrentUserDep,
    task_id: int,
):
    """
    通过 SSE 获取研究任务实时进度.

    使用 Redis Pub/Sub 接收 Worker 推送的消息.
    """
    # 验证任务归属
    result = await db.execute(
        select(ResearchTask).where(
            ResearchTask.id == task_id,
            ResearchTask.user_id == current_user.id,
        )
    )
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    channel = f"research:{task_id}"

    async def event_generator():
        """生成 SSE 事件流."""
        pubsub = await subscribe_channel(channel)

        try:
            # 发送初始状态
            yield f"event: status\ndata: {json.dumps({'status': task.status})}\n\n"

            # 监听 Redis 消息
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    event_type = data.get("event", "message")

                    yield f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

                    # 任务完成或出错时结束
                    if event_type in ("complete", "error"):
                        break

        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Task-Id": str(task_id),
        },
    )


@router.post("/stream")
async def research_stream_legacy(
    db: DBDep,
    current_user: CurrentUserDep,
    request: ResearchRequest,
):
    """
    流式研究接口 (SSE) - 直接执行版本.

    注意: 推荐使用 /tasks + /tasks/{id}/stream 接口.
    """
    if not request.query:
        raise HTTPException(status_code=422, detail="Query is required")

    # 获取或创建会话
    if request.session_id:
        result = await db.execute(
            select(Session).where(
                Session.id == request.session_id,
                Session.user_id == current_user.id,
            )
        )
        session = result.scalar_one_or_none()
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = Session(
            user_id=current_user.id,
            title=request.query[:50] + "..." if len(request.query) > 50 else request.query,
            mode="research",
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

    # 创建研究任务记录
    task = ResearchTask(
        session_id=session.id,
        user_id=current_user.id,
        query=request.query,
        config=request.config.model_dump() if request.config else {},
        status="running",
        started_at=datetime.utcnow(),
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)

    async def generate_stream():
        try:
            agent = ResearchAgent(request.config or ResearchConfig())

            async for event in agent._core.stream_research(request.query, current_user.id):
                yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"

            # 更新任务状态
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            task.iterations = 1  # 简化统计
            await db.commit()

        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            await db.commit()
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Session-Id": str(session.id),
            "X-Task-Id": str(task.id),
        },
    )


@router.get("/tasks/{task_id}", response_model=ResearchTaskDetail)
async def get_research_task(
    db: DBDep,
    current_user: CurrentUserDep,
    task_id: int,
):
    """获取研究任务详情."""
    result = await db.execute(
        select(ResearchTask).where(
            ResearchTask.id == task_id,
            ResearchTask.user_id == current_user.id,
        )
    )
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.get("/tasks", response_model=list[ResearchTaskResponse])
async def list_research_tasks(
    db: DBDep,
    current_user: CurrentUserDep,
    session_id: int | None = None,
    limit: int = 10,
    offset: int = 0,
):
    """获取研究任务列表."""
    query = select(ResearchTask).where(
        ResearchTask.user_id == current_user.id,
    )

    if session_id:
        query = query.where(ResearchTask.session_id == session_id)

    query = query.order_by(ResearchTask.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    tasks = result.scalars().all()

    return tasks
