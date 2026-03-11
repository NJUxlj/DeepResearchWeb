"""消息相关 Pydantic Schema."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Citation(BaseModel):
    """引用信息 Schema."""

    id: str
    index: int
    url: str
    title: str
    snippet: str
    source_type: str  # "web" | "mcp" | "memory" | "document"
    favicon: str | None = None


class MessageBase(BaseModel):
    """消息基础 Schema."""

    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)


class MessageCreate(MessageBase):
    """创建消息请求 Schema."""

    session_id: int
    citations: list[Citation] | None = None
    meta_info: dict[str, Any] | None = None


class MessageUpdate(BaseModel):
    """更新消息请求 Schema."""

    content: str | None = Field(None, min_length=1)


class MessageResponse(MessageBase):
    """消息响应 Schema."""

    id: int
    session_id: int
    thinking: str | None = None
    citations: list[Citation] | None = None
    meta_info: dict[str, Any] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageListResponse(BaseModel):
    """消息列表响应 Schema."""

    messages: list[MessageResponse]
    total: int


class ChatRequest(BaseModel):
    """聊天请求 Schema."""

    session_id: int | None = None
    message: str = Field(..., min_length=1)
    stream: bool = True


class ChatStreamEvent(BaseModel):
    """SSE 流式事件 Schema."""

    event: str  # "message", "chunk", "citations", "error", "done"
    data: dict[str, Any]
