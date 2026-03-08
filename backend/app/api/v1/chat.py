"""基础聊天 API 端点（支持 SSE 流式响应）."""

import json
from datetime import datetime
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from app.agents.chat_agent import ChatAgent
from app.api.deps import CurrentUserDep, DBDep
from app.models.message import Message
from app.models.session import Session
from app.schemas.message import ChatRequest, Citation

router = APIRouter(prefix="/chat", tags=["chat"])


async def generate_chat_stream(
    db: DBDep,
    session: Session,
    user_message: str,
) -> AsyncGenerator[str, None]:
    """
    生成聊天流式响应.

    Yields SSE 格式的事件流.
    """
    try:
        # 保存用户消息
        user_msg = Message(
            session_id=session.id,
            role="user",
            content=user_message,
        )
        db.add(user_msg)
        await db.commit()

        # 发送用户消息确认
        yield f"event: message\ndata: {json.dumps({'role': 'user', 'content': user_message})}\n\n"

        # 获取历史消息用于上下文
        result = await db.execute(
            select(Message)
            .where(Message.session_id == session.id)
            .order_by(Message.created_at.desc())
            .limit(20)
        )
        history = list(reversed(result.scalars().all()))

        # 调用 Chat Agent 获取流式响应
        chat_agent = ChatAgent()
        assistant_content = ""
        citations: list[Citation] = []

        async for chunk in chat_agent.stream_chat(
            message=user_message,
            history=[
                {"role": m.role, "content": m.content}
                for m in history[:-1]  # 排除刚添加的用户消息
            ],
        ):
            if chunk["type"] == "content":
                assistant_content += chunk["content"]
                yield f"event: chunk\ndata: {json.dumps({'content': chunk['content']})}\n\n"

            elif chunk["type"] == "citations":
                citations = chunk["citations"]

        # 保存助手消息
        citations_data = [c.model_dump() for c in citations] if citations else None
        assistant_msg = Message(
            session_id=session.id,
            role="assistant",
            content=assistant_content,
            citations=citations_data,
        )
        db.add(assistant_msg)
        await db.commit()

        # 发送完成事件
        yield f"event: done\ndata: {json.dumps({'message_id': assistant_msg.id})}\n\n"

        # 如果有引用，发送引用信息
        if citations:
            yield f"event: citations\ndata: {json.dumps({'citations': citations_data})}\n\n"

    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"


@router.get("/stream")
async def chat_stream(
    db: DBDep,
    current_user: CurrentUserDep,
    session_id: int | None = None,
    message: str = "",
    stream: bool = True,
):
    """
    流式聊天接口 (SSE).

    如果提供了 session_id，则继续已有会话；
    否则创建新会话。
    """
    if not message:
        raise HTTPException(status_code=422, detail="Message is required")

    # 获取或创建会话
    if session_id:
        result = await db.execute(
            select(Session).where(
                Session.id == session_id,
                Session.user_id == current_user.id,
            )
        )
        session = result.scalar_one_or_none()

        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        # 创建新会话，标题使用用户消息的前 50 字符
        title = message[:50] + "..." if len(message) > 50 else message
        session = Session(
            user_id=current_user.id,
            title=title,
            mode="chat",
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

    # 更新会话更新时间
    session.updated_at = datetime.utcnow()
    await db.commit()

    # 返回 SSE 流
    return StreamingResponse(
        generate_chat_stream(db, session, message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Session-Id": str(session.id),
        },
    )


@router.post("/message")
async def send_message(
    db: DBDep,
    current_user: CurrentUserDep,
    request: ChatRequest,
):
    """
    非流式聊天接口（简单响应）.
    """
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
        title = request.message[:50] + "..." if len(request.message) > 50 else request.message
        session = Session(
            user_id=current_user.id,
            title=title,
            mode="chat",
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

    # 保存用户消息
    user_msg = Message(
        session_id=session.id,
        role="user",
        content=request.message,
    )
    db.add(user_msg)
    await db.commit()

    # 获取历史
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session.id)
        .order_by(Message.created_at.desc())
        .limit(20)
    )
    history = list(reversed(result.scalars().all()))

    # 调用 Chat Agent
    chat_agent = ChatAgent()
    response = await chat_agent.chat(
        message=request.message,
        history=[
            {"role": m.role, "content": m.content}
            for m in history[:-1]
        ],
    )

    # 保存助手消息
    citations_data = [c.model_dump() for c in response["citations"]] if response["citations"] else None
    assistant_msg = Message(
        session_id=session.id,
        role="assistant",
        content=response["content"],
        citations=citations_data,
    )
    db.add(assistant_msg)
    await db.commit()
    await db.refresh(assistant_msg)

    return {
        "message_id": assistant_msg.id,
        "content": response["content"],
        "citations": citations_data,
        "session_id": session.id,
    }
