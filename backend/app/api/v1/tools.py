"""工具配置 API."""

from datetime import datetime

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import CurrentUserDep, DBDep
from app.models.tool_config import ToolConfig
from pydantic import BaseModel

from app.schemas.tool import (
    ToolConfigCreate,
    ToolConfigResponse,
    ToolConfigUpdate,
)

router = APIRouter(prefix="/tools", tags=["tools"])

BUILTIN_TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web for information",
        "tool_type": "builtin",
        "config": {
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 5,
                    },
                },
                "required": ["query"],
            }
        },
    },
    {
        "name": "url_fetch",
        "description": "Fetch content from a URL",
        "tool_type": "builtin",
        "config": {
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch"},
                    "selector": {
                        "type": "string",
                        "description": "CSS selector to extract content (optional)",
                    },
                },
                "required": ["url"],
            }
        },
    },
    {
        "name": "code_execute",
        "description": "Execute Python code in a sandboxed environment (placeholder)",
        "tool_type": "builtin",
        "config": {
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"},
                    "timeout": {
                        "type": "integer",
                        "description": "Execution timeout in seconds",
                        "default": 30,
                    },
                },
                "required": ["code"],
            }
        },
    },
    {
        "name": "file_read",
        "description": "Read content from a file (placeholder)",
        "tool_type": "builtin",
        "config": {
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"},
                    "encoding": {
                        "type": "string",
                        "description": "File encoding",
                        "default": "utf-8",
                    },
                },
                "required": ["path"],
            }
        },
    },
]


class ToolListResponse(BaseModel):
    items: list[ToolConfigResponse]
    total: int


@router.get("", response_model=ToolListResponse)
async def list_tools(
    db: DBDep,
    current_user: CurrentUserDep,
):
    """获取用户工具配置列表（包含内置工具）."""
    # 获取自定义工具
    result = await db.execute(
        select(ToolConfig).where(ToolConfig.user_id == current_user.id)
    )
    custom_tools = result.scalars().all()

    # 合并内置工具
    all_tools = [
        ToolConfigResponse(
            id=0,
            user_id=current_user.id,
            name=tool["name"],
            description=tool["description"],
            tool_type="builtin",
            config=tool["config"],
            enabled=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        for tool in BUILTIN_TOOLS
    ]
    all_tools.extend(custom_tools)

    return ToolListResponse(
        items=all_tools,
        total=len(all_tools)
    )


@router.post("", response_model=ToolConfigResponse, status_code=201)
async def create_tool(
    db: DBDep,
    current_user: CurrentUserDep,
    data: ToolConfigCreate,
):
    """创建自定义工具配置."""
    tool = ToolConfig(
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        tool_type=data.tool_type,
        config=data.config,
        enabled=data.enabled,
    )
    db.add(tool)
    await db.commit()
    await db.refresh(tool)
    return tool


@router.put("/{tool_id}", response_model=ToolConfigResponse)
async def update_tool(
    db: DBDep,
    current_user: CurrentUserDep,
    tool_id: int,
    data: ToolConfigUpdate,
):
    """更新工具配置."""
    result = await db.execute(
        select(ToolConfig).where(
            ToolConfig.id == tool_id,
            ToolConfig.user_id == current_user.id,
        )
    )
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tool, field, value)

    await db.commit()
    await db.refresh(tool)
    return tool


@router.delete("/{tool_id}", status_code=204)
async def delete_tool(
    db: DBDep,
    current_user: CurrentUserDep,
    tool_id: int,
):
    """删除工具配置."""
    result = await db.execute(
        select(ToolConfig).where(
            ToolConfig.id == tool_id,
            ToolConfig.user_id == current_user.id,
        )
    )
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    await db.delete(tool)
    await db.commit()


@router.patch("/{tool_id}/toggle", response_model=ToolConfigResponse)
async def toggle_tool(
    db: DBDep,
    current_user: CurrentUserDep,
    tool_id: int,
    data: dict,
):
    """启用/禁用工具."""
    # 内置工具不支持 toggle
    if tool_id == 0:
        raise HTTPException(status_code=400, detail="Cannot toggle builtin tools")

    result = await db.execute(
        select(ToolConfig).where(
            ToolConfig.id == tool_id,
            ToolConfig.user_id == current_user.id,
        )
    )
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    tool.enabled = data.get("enabled", not tool.enabled)
    await db.commit()
    await db.refresh(tool)
    return tool
