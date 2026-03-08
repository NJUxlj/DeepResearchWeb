"""MCP 相关 Schema."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator


class MCPServerConfigBase(BaseModel):
    """MCP 服务器配置基础 Schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    transport: str = Field(..., pattern="^(stdio|sse)$")

    # stdio 配置
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)

    # sse 配置
    url: str | None = None

    enabled: bool = True

    @model_validator(mode="after")
    def validate_transport_config(self):
        """验证传输类型与配置的匹配性."""
        if self.transport == "stdio" and not self.command:
            raise ValueError("command is required for stdio transport")
        if self.transport == "sse" and not self.url:
            raise ValueError("url is required for sse transport")
        return self


class MCPServerConfigCreate(MCPServerConfigBase):
    """创建 MCP 服务器配置."""

    pass


class MCPServerConfigUpdate(BaseModel):
    """更新 MCP 服务器配置."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    command: str | None = None
    args: list[str] | None = None
    env: dict[str, str] | None = None
    url: str | None = None
    enabled: bool | None = None


class MCPServerConfigResponse(MCPServerConfigBase):
    """MCP 服务器配置响应."""

    id: int
    user_id: int
    cached_tools: list[dict[str, Any]] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MCPTool(BaseModel):
    """MCP 工具定义."""

    name: str
    description: str
    parameters: dict[str, Any]


class MCPServerToolsResponse(BaseModel):
    """MCP 服务器工具列表响应."""

    server_id: int
    server_name: str
    tools: list[MCPTool]
    cached: bool = False
