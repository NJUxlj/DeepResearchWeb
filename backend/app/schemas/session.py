"""会话相关 Pydantic Schema."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.message import MessageResponse


class SessionBase(BaseModel):
    """会话基础 Schema."""

    title: str = Field(..., min_length=1, max_length=255)
    mode: str = Field(default="chat", pattern="^(chat|research)$")


class SessionCreate(SessionBase):
    """创建会话请求 Schema."""

    pass


class SessionUpdate(BaseModel):
    """更新会话请求 Schema."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)


class SessionResponse(SessionBase):
    """会话响应 Schema."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


class SessionDetailResponse(SessionResponse):
    """会话详情响应（包含消息列表）."""

    messages: list[MessageResponse] = []


class SessionListResponse(BaseModel):
    """会话列表响应."""

    items: list[SessionResponse]
    total: int
    page: int
    page_size: int
