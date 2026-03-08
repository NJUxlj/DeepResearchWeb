"""MCP 服务器配置 API."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import CurrentUserDep, DBDep
from app.models.mcp_config import MCPServerConfig
from app.schemas.mcp import (
    MCPServerConfigCreate,
    MCPServerConfigResponse,
    MCPServerConfigUpdate,
    MCPServerToolsResponse,
)
from app.services.mcp_service import mcp_service

router = APIRouter(prefix="/mcp", tags=["mcp"])


class MCPServerListResponse(BaseModel):
    items: list[MCPServerConfigResponse]
    total: int


@router.get("/servers", response_model=MCPServerListResponse)
async def list_mcp_servers(
    db: DBDep,
    current_user: CurrentUserDep,
):
    """获取用户 MCP 服务器配置列表."""
    result = await db.execute(
        select(MCPServerConfig).where(MCPServerConfig.user_id == current_user.id)
    )
    servers = result.scalars().all()
    return MCPServerListResponse(
        items=servers,
        total=len(servers)
    )


@router.post("/servers", response_model=MCPServerConfigResponse, status_code=201)
async def create_mcp_server(
    db: DBDep,
    current_user: CurrentUserDep,
    data: MCPServerConfigCreate,
):
    """创建 MCP 服务器配置."""
    server = MCPServerConfig(
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        transport=data.transport,
        command=data.command,
        args=data.args,
        env=data.env,
        url=data.url,
        enabled=data.enabled,
    )
    db.add(server)
    await db.commit()
    await db.refresh(server)
    return server


@router.put("/servers/{server_id}", response_model=MCPServerConfigResponse)
async def update_mcp_server(
    db: DBDep,
    current_user: CurrentUserDep,
    server_id: int,
    data: MCPServerConfigUpdate,
):
    """更新 MCP 服务器配置."""
    result = await db.execute(
        select(MCPServerConfig).where(
            MCPServerConfig.id == server_id,
            MCPServerConfig.user_id == current_user.id,
        )
    )
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(server, field, value)

    await db.commit()
    await db.refresh(server)
    return server


@router.patch("/servers/{server_id}/toggle", response_model=MCPServerConfigResponse)
async def toggle_mcp_server(
    db: DBDep,
    current_user: CurrentUserDep,
    server_id: int,
    data: dict,
):
    """启用/禁用 MCP 服务器."""
    result = await db.execute(
        select(MCPServerConfig).where(
            MCPServerConfig.id == server_id,
            MCPServerConfig.user_id == current_user.id,
        )
    )
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    server.enabled = data.get("enabled", not server.enabled)
    await db.commit()
    await db.refresh(server)
    return server


@router.post("/servers/{server_id}/test")
async def test_mcp_server(
    db: DBDep,
    current_user: CurrentUserDep,
    server_id: int,
):
    """测试 MCP 服务器连接."""
    result = await db.execute(
        select(MCPServerConfig).where(
            MCPServerConfig.id == server_id,
            MCPServerConfig.user_id == current_user.id,
        )
    )
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    try:
        await mcp_service.connect(server)
        return {"success": True, "message": "Connection successful"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.get("/servers/{server_id}/tools", response_model=MCPServerToolsResponse)
async def get_mcp_server_tools(
    db: DBDep,
    current_user: CurrentUserDep,
    server_id: int,
):
    """
    获取 MCP 服务器的工具列表.

    会尝试连接服务器并获取最新工具列表，同时更新缓存.
    """
    result = await db.execute(
        select(MCPServerConfig).where(
            MCPServerConfig.id == server_id,
            MCPServerConfig.user_id == current_user.id,
        )
    )
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    try:
        # 连接服务器获取工具列表
        tools = await mcp_service.connect(server)

        # 更新缓存
        server.cached_tools = tools
        await db.commit()

        return MCPServerToolsResponse(
            server_id=server.id,
            server_name=server.name,
            tools=tools,
            cached=False,
        )

    except Exception as e:
        # 如果连接失败，返回缓存的工具（如果有）
        if server.cached_tools:
            return MCPServerToolsResponse(
                server_id=server.id,
                server_name=server.name,
                tools=server.cached_tools,
                cached=True,
            )
        raise HTTPException(status_code=502, detail=f"Failed to connect: {e}")


@router.delete("/servers/{server_id}", status_code=204)
async def delete_mcp_server(
    db: DBDep,
    current_user: CurrentUserDep,
    server_id: int,
):
    """删除 MCP 服务器配置."""
    result = await db.execute(
        select(MCPServerConfig).where(
            MCPServerConfig.id == server_id,
            MCPServerConfig.user_id == current_user.id,
        )
    )
    server = result.scalar_one_or_none()
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")

    # 断开连接
    await mcp_service.disconnect(server_id)

    await db.delete(server)
    await db.commit()
