"""会话管理 API 端点."""

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import desc, func, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUserDep, DBDep
from app.models.message import Message
from app.models.session import Session
from app.schemas.session import (
    SessionCreate,
    SessionDetailResponse,
    SessionListResponse,
    SessionResponse,
    SessionUpdate,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get(
    "",
    response_model=SessionListResponse,
    summary="获取会话列表",
)
async def list_sessions(
    db: DBDep,
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    mode: str | None = Query(None, regex="^(chat|research)$"),
) -> dict:
    """获取当前用户的会话列表（分页）."""
    # 构建查询
    query = select(Session).where(Session.user_id == current_user.id)

    if mode:
        query = query.where(Session.mode == mode)

    # 统计总数
    count_query = select(func.count()).select_from(Session).where(
        Session.user_id == current_user.id
    )
    if mode:
        count_query = count_query.where(Session.mode == mode)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # 分页查询
    query = query.order_by(desc(Session.updated_at))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    sessions = result.scalars().all()

    # 获取每个会话的消息数量
    session_ids = [s.id for s in sessions]
    msg_count_query = (
        select(Message.session_id, func.count().label("count"))
        .where(Message.session_id.in_(session_ids))
        .group_by(Message.session_id)
    )
    msg_count_result = await db.execute(msg_count_query)
    msg_counts = {row.session_id: row.count for row in msg_count_result.all()}

    # 构建响应
    items = []
    for session in sessions:
        session_dict = {
            "id": session.id,
            "user_id": session.user_id,
            "title": session.title,
            "mode": session.mode,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "message_count": msg_counts.get(session.id, 0),
        }
        items.append(session_dict)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建新会话",
)
async def create_session(
    db: DBDep,
    current_user: CurrentUserDep,
    data: SessionCreate,
) -> Session:
    """创建新会话."""
    session = Session(
        user_id=current_user.id,
        title=data.title,
        mode=data.mode,
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return session


@router.get(
    "/{session_id}",
    response_model=SessionDetailResponse,
    summary="获取会话详情",
)
async def get_session(
    db: DBDep,
    current_user: CurrentUserDep,
    session_id: int,
) -> Session:
    """获取会话详情（包含消息列表）."""
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id, Session.user_id == current_user.id)
        .options(selectinload(Session.messages))
    )
    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return session


@router.put(
    "/{session_id}",
    response_model=SessionResponse,
    summary="更新会话",
)
async def update_session(
    db: DBDep,
    current_user: CurrentUserDep,
    session_id: int,
    data: SessionUpdate,
) -> Session:
    """更新会话信息（如标题）."""
    result = await db.execute(
        select(Session).where(
            Session.id == session_id,
            Session.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if data.title is not None:
        session.title = data.title

    await db.commit()
    await db.refresh(session)

    return session


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除会话",
)
async def delete_session(
    db: DBDep,
    current_user: CurrentUserDep,
    session_id: int,
) -> None:
    """删除会话及其所有消息."""
    result = await db.execute(
        select(Session).where(
            Session.id == session_id,
            Session.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    await db.delete(session)
    await db.commit()
