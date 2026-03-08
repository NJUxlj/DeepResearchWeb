"""消息管理 API 端点."""

from fastapi import APIRouter, status
from sqlalchemy import func, select

from app.api.deps import CurrentUserDep, DBDep
from app.core.exceptions import NotFoundException
from app.models.message import Message
from app.models.session import Session
from app.schemas.message import (
    MessageCreate,
    MessageListResponse,
    MessageResponse,
    MessageUpdate,
)

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post(
    "",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建消息",
)
async def create_message(
    db: DBDep,
    current_user: CurrentUserDep,
    data: MessageCreate,
) -> Message:
    """在指定会话中创建新消息."""
    # 验证会话归属
    result = await db.execute(
        select(Session).where(
            Session.id == data.session_id,
            Session.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if session is None:
        raise NotFoundException("Session not found")

    # 创建消息
    message = Message(
        session_id=data.session_id,
        role=data.role,
        content=data.content,
    )
    db.add(message)

    # 更新会话的 updated_at 时间戳
    session.updated_at = func.now()

    await db.commit()
    await db.refresh(message)
    return message


@router.get(
    "/by-session/{session_id}",
    response_model=MessageListResponse,
    summary="获取会话消息列表",
)
async def list_messages(
    db: DBDep,
    current_user: CurrentUserDep,
    session_id: int,
    limit: int = 100,
    offset: int = 0,
) -> MessageListResponse:
    """获取指定会话的所有消息列表."""
    # 验证会话归属
    result = await db.execute(
        select(Session).where(
            Session.id == session_id,
            Session.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if session is None:
        raise NotFoundException("Session not found")

    # 查询消息
    msg_result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
        .offset(offset)
    )
    messages = msg_result.scalars().all()

    # 统计总数
    count_result = await db.execute(
        select(func.count(Message.id)).where(Message.session_id == session_id)
    )
    total = count_result.scalar() or 0

    return MessageListResponse(messages=messages, total=total)


@router.get(
    "/{message_id}",
    response_model=MessageResponse,
    summary="获取消息详情",
)
async def get_message(
    db: DBDep,
    current_user: CurrentUserDep,
    message_id: int,
) -> Message:
    """获取指定消息的详情."""
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()

    if message is None:
        raise NotFoundException("Message not found")

    # 验证会话归属
    session_result = await db.execute(
        select(Session).where(
            Session.id == message.session_id,
            Session.user_id == current_user.id,
        )
    )
    session = session_result.scalar_one_or_none()

    if session is None:
        raise NotFoundException("Message not found")

    return message


@router.put(
    "/{message_id}",
    response_model=MessageResponse,
    summary="更新消息",
)
async def update_message(
    db: DBDep,
    current_user: CurrentUserDep,
    message_id: int,
    data: MessageUpdate,
) -> Message:
    """更新消息内容."""
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()

    if message is None:
        raise NotFoundException("Message not found")

    # 验证会话归属
    session_result = await db.execute(
        select(Session).where(
            Session.id == message.session_id,
            Session.user_id == current_user.id,
        )
    )
    session = session_result.scalar_one_or_none()

    if session is None:
        raise NotFoundException("Message not found")

    if data.content is not None:
        message.content = data.content

    if data.citations_json is not None:
        message.citations_json = data.citations_json

    await db.commit()
    await db.refresh(message)
    return message


@router.delete(
    "/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除消息",
)
async def delete_message(
    db: DBDep,
    current_user: CurrentUserDep,
    message_id: int,
) -> None:
    """删除指定消息."""
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    message = result.scalar_one_or_none()

    if message is None:
        raise NotFoundException("Message not found")

    # 验证会话归属
    session_result = await db.execute(
        select(Session).where(
            Session.id == message.session_id,
            Session.user_id == current_user.id,
        )
    )
    session = session_result.scalar_one_or_none()

    if session is None:
        raise NotFoundException("Message not found")

    await db.delete(message)
    await db.commit()
