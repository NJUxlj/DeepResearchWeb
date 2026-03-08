"""Pydantic schemas."""

from app.schemas.message import (
    ChatRequest,
    ChatStreamEvent,
    Citation,
    MessageCreate,
    MessageListResponse,
    MessageResponse,
    MessageUpdate,
)
from app.schemas.research import (
    ResearchConfig,
    ResearchIteration,
    ResearchRequest,
    ResearchResult,
    ResearchStreamEvent,
    ResearchTaskDetail,
    ResearchTaskResponse,
    SearchResult,
    SubQuery,
)
from app.schemas.session import SessionCreate, SessionResponse, SessionUpdate
from app.schemas.user import Token, UserCreate, UserResponse
from app.schemas.tool import (
    ToolConfigBase,
    ToolConfigCreate,
    ToolConfigResponse,
    ToolConfigUpdate,
    ToolDefinition,
)
from app.schemas.skill import (
    SkillConfigBase,
    SkillConfigCreate,
    SkillConfigResponse,
    SkillConfigUpdate,
)
from app.schemas.mcp import (
    MCPServerConfigBase,
    MCPServerConfigCreate,
    MCPServerConfigResponse,
    MCPServerConfigUpdate,
    MCPTool,
    MCPServerToolsResponse,
)

__all__ = [
    # Message schemas
    "ChatRequest",
    "ChatStreamEvent",
    "Citation",
    "MessageCreate",
    "MessageListResponse",
    "MessageResponse",
    "MessageUpdate",
    # Research schemas
    "ResearchConfig",
    "ResearchIteration",
    "ResearchRequest",
    "ResearchResult",
    "ResearchStreamEvent",
    "ResearchTaskDetail",
    "ResearchTaskResponse",
    "SearchResult",
    "SubQuery",
    # Session schemas
    "SessionCreate",
    "SessionResponse",
    "SessionUpdate",
    # User schemas
    "Token",
    "UserCreate",
    "UserResponse",
    # Tool schemas
    "ToolConfigBase",
    "ToolConfigCreate",
    "ToolConfigResponse",
    "ToolConfigUpdate",
    "ToolDefinition",
    # Skill schemas
    "SkillConfigBase",
    "SkillConfigCreate",
    "SkillConfigResponse",
    "SkillConfigUpdate",
    # MCP schemas
    "MCPServerConfigBase",
    "MCPServerConfigCreate",
    "MCPServerConfigResponse",
    "MCPServerConfigUpdate",
    "MCPTool",
    "MCPServerToolsResponse",
]
