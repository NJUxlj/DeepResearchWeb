"""工具相关 Schema."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ToolConfigBase(BaseModel):
    """工具配置基础 Schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str
    tool_type: str = Field(..., pattern="^(builtin|custom)$")
    config: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class ToolConfigCreate(ToolConfigBase):
    """创建工具配置."""

    pass


class ToolConfigUpdate(BaseModel):
    """更新工具配置."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    config: dict[str, Any] | None = None
    enabled: bool | None = None


class ToolConfigResponse(ToolConfigBase):
    """工具配置响应."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ToolDefinition(BaseModel):
    """工具定义（OpenAI Function Calling 格式）."""

    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema
