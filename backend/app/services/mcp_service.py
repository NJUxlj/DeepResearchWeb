"""MCP 服务实现.

使用全局 mcp_pool 实例进行 MCP 服务器管理。
"""

from typing import Any

from app.models.mcp_config import MCPServerConfig


class MCPService:
    """MCP 服务 - 连接到 MCP Server 并获取工具列表."""

    def __init__(self):
        self._sessions: dict[int, dict[str, Any]] = {}

    async def connect(self, server_config: MCPServerConfig) -> list[dict[str, Any]]:
        """连接到 MCP Server 并获取工具列表.

        Args:
            server_config: MCP 服务器配置

        Returns:
            工具列表
        """
        try:
            from mcp import ClientSession
            from mcp.client.stdio import stdio_client

            if server_config.transport == "stdio":
                params = {
                    "command": server_config.command or "",
                    "args": server_config.args or [],
                    "env": server_config.env or None,
                }

                # 创建 stdio 客户端
                read, write = await stdio_client(params).__aenter__()
                session = await ClientSession(read, write).__aenter__()
                await session.initialize()

                # 获取工具列表
                tools_result = await session.list_tools()
                tools = [
                    {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.parameters,
                    }
                    for tool in tools_result.tools
                ]

                # 保存会话
                self._sessions[server_config.id] = {
                    "session": session,
                    "read": read,
                    "write": write,
                }

                return tools

            elif server_config.transport == "sse":
                # SSE 传输实现
                # 使用 SSE 客户端连接到 MCP 服务器
                return await self._connect_sse(server_config)

            return []

        except ImportError:
            # 如果 mcp 包未安装，返回空列表
            return []
        except Exception as e:
            # 记录错误但返回空列表
            print(f"MCP connection error: {e}")
            return []

    async def _connect_sse(
        self,
        server_config: MCPServerConfig,
    ) -> list[dict[str, Any]]:
        """通过 SSE 连接到 MCP Server.

        Args:
            server_config: MCP 服务器配置

        Returns:
            工具列表
        """
        import httpx

        if not server_config.url:
            return []

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 通过 SSE 端点获取工具列表
                response = await client.get(f"{server_config.url}/tools")
                response.raise_for_status()
                return response.json().get("tools", [])
            except Exception:
                return []

    async def call_tool(
        self,
        server_id: int,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """调用 MCP 工具.

        Args:
            server_id: 服务器 ID
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果
        """
        session_data = self._sessions.get(server_id)
        if not session_data:
            raise ValueError(f"MCP server {server_id} not connected")

        session = session_data["session"]
        result = await session.call_tool(tool_name, arguments)
        return result

    async def disconnect(self, server_id: int) -> None:
        """断开 MCP Server 连接.

        Args:
            server_id: 服务器 ID
        """
        if server_id in self._sessions:
            session_data = self._sessions.pop(server_id)
            try:
                await session_data["session"].__aexit__(None, None, None)
                await session_data["write"].__aexit__(None, None, None)
            except Exception:
                pass

    async def disconnect_all(self) -> None:
        """断开所有连接."""
        for server_id in list(self._sessions.keys()):
            await self.disconnect(server_id)


# 全局 MCP 服务实例
mcp_service = MCPService()
