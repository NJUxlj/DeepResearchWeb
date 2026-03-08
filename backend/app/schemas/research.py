"""Research 相关 Pydantic Schema."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.message import Citation


class ResearchConfig(BaseModel):
    """研究配置."""

    max_iterations: int = Field(default=3, ge=1, le=5)
    search_depth: str = Field(default="standard", pattern="^(quick|standard|deep)$")
    include_memory: bool = True
    include_web: bool = True
    include_mcp: bool = True


class SubQuery(BaseModel):
    """子查询（由 Planner 生成）."""

    id: str
    query: str
    strategy: str  # "web_search" | "memory_search" | "mcp_call" | "tool_call"
    target: str | None = None  # 具体目标（如 MCP 服务器名、工具名）
    priority: int = 1  # 1-5


class SearchResult(BaseModel):
    """搜索结果."""

    source: str  # 来源标识
    source_type: str  # "web" | "memory" | "mcp" | "tool"
    content: str
    url: str | None = None
    title: str | None = None
    relevance_score: float = 0.0
    metadata: dict[str, Any] = {}


class ResearchIteration(BaseModel):
    """研究迭代记录."""

    iteration: int
    sub_queries: list[SubQuery]
    search_results: list[SearchResult]
    synthesis: str
    needs_more_info: bool


class ResearchResult(BaseModel):
    """研究结果."""

    query: str
    iterations: list[ResearchIteration]
    final_report: str
    citations: list[Citation]
    total_sources: int
    completed_at: datetime


class ResearchTaskResponse(BaseModel):
    """研究任务响应."""

    id: int
    session_id: int
    status: str
    query: str
    iterations: int
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class ResearchTaskDetail(ResearchTaskResponse):
    """研究任务详情."""

    result: ResearchResult | None = None
    error: str | None = None


class ResearchStreamEvent(BaseModel):
    """研究流式事件."""

    event: str  # "start", "plan", "search", "synthesis", "citations", "complete", "error"
    data: dict[str, Any]


class ResearchRequest(BaseModel):
    """研究请求."""

    query: str = Field(..., min_length=1)
    session_id: int | None = None
    config: ResearchConfig | None = None
