"""工具执行服务."""

import asyncio
import re
from typing import Any

import httpx

# 内置工具定义
BUILTIN_TOOLS = {
    "web_search": {
        "name": "web_search",
        "description": "Search the web for information using Tavily search engine",
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
        },
    },
    "url_fetch": {
        "name": "url_fetch",
        "description": "Fetch content from a URL (web page)",
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
        },
    },
    "code_execute": {
        "name": "code_execute",
        "description": "Execute Python code in a sandboxed environment (placeholder)",
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
        },
    },
    "file_read": {
        "name": "file_read",
        "description": "Read content from a file (placeholder)",
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
        },
    },
}


class ToolService:
    """工具执行服务."""

    async def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """执行工具.

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果
        """
        if tool_name == "web_search":
            return await self._web_search(**arguments)
        elif tool_name == "url_fetch":
            return await self._url_fetch(**arguments)
        elif tool_name == "code_execute":
            return await self._code_execute(**arguments)
        elif tool_name == "file_read":
            return await self._file_read(**arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def _web_search(
        self,
        query: str,
        max_results: int = 5,
    ) -> dict[str, Any]:
        """执行 Web 搜索.

        使用 Tavily 搜索 API。
        """
        try:
            from app.config import settings

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": settings.TAVILY_API_KEY,
                        "query": query,
                        "max_results": max_results,
                    },
                )
                response.raise_for_status()
                data = response.json()

                return {
                    "results": [
                        {
                            "title": result.get("title", ""),
                            "url": result.get("url", ""),
                            "content": result.get("content", ""),
                            "score": result.get("score", 0),
                        }
                        for result in data.get("results", [])
                    ],
                    "query": query,
                }
        except Exception as e:
            return {"error": str(e), "results": []}

    async def _url_fetch(
        self,
        url: str,
        selector: str | None = None,
    ) -> dict[str, Any]:
        """获取 URL 内容.

        Args:
            url: 要获取的 URL
            selector: 可选的 CSS 选择器

        Returns:
            页面内容
        """
        try:
            async with httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; DeepResearchWeb/1.0)"
                },
            ) as client:
                response = await client.get(url)
                response.raise_for_status()

                content_type = response.headers.get("content-type", "")

                if "text/html" in content_type:
                    # 简单的 HTML 解析，提取文本
                    html = response.text
                    # 移除脚本和样式
                    html = re.sub(
                        r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL
                    )
                    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)

                    if selector:
                        # 简单的 CSS 选择器支持
                        pattern = rf"<({selector.replace('.', '').replace('#', '')}|{selector.lstrip('.#')})[^>]*>(.*?)</\1>"
                        matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
                        text = "\n".join([m[1] for m in matches]) if matches else ""
                    else:
                        # 提取纯文本
                        text = re.sub(r"<[^>]+>", "", html)
                        text = re.sub(r"\s+", " ", text).strip()

                    return {
                        "url": url,
                        "content": text[:10000],  # 限制内容长度
                        "content_type": content_type,
                    }
                else:
                    return {
                        "url": url,
                        "content": response.text[:10000],
                        "content_type": content_type,
                    }
        except Exception as e:
            return {"error": str(e), "url": url}

    async def _code_execute(
        self,
        code: str,
        timeout: int = 30,
    ) -> dict[str, Any]:
        """执行 Python 代码（占位实现）.

        注意：生产环境需要使用沙箱环境执行。
        """
        return {
            "error": "code_execute is a placeholder - not implemented",
            "code": code,
        }

    async def _file_read(
        self,
        path: str,
        encoding: str = "utf-8",
    ) -> dict[str, Any]:
        """读取文件（占位实现）.

        注意：生产环境需要实现安全检查。
        """
        return {
            "error": "file_read is a placeholder - not implemented",
            "path": path,
        }

    def get_tool_definition(self, tool_name: str) -> dict[str, Any] | None:
        """获取工具定义（OpenAI Function Calling 格式）."""
        return BUILTIN_TOOLS.get(tool_name)

    def list_builtin_tools(self) -> list[dict[str, Any]]:
        """列出所有内置工具."""
        return list(BUILTIN_TOOLS.values())


# 全局工具服务实例
tool_service = ToolService()
