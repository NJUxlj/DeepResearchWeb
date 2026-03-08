"""Searcher: 多源并行检索."""

import asyncio
from typing import Any

from tavily import AsyncTavilyClient

from app.config import settings
from app.schemas.research import SearchResult, SubQuery


class ResearchSearcher:
    """研究搜索器，支持多源并行检索."""

    def __init__(self):
        self.tavily_client = (
            AsyncTavilyClient(api_key=settings.TAVILY_API_KEY)
            if settings.TAVILY_API_KEY
            else None
        )

    async def search(
        self,
        sub_queries: list[SubQuery],
        user_id: int | None = None,
    ) -> list[SearchResult]:
        """
        并行执行多个子查询的检索.

        Args:
            sub_queries: 子查询列表
            user_id: 用户 ID（用于记忆检索）

        Returns:
            搜索结果列表
        """
        tasks = []
        for sq in sub_queries:
            task = self._execute_search(sq, user_id)
            tasks.append(task)

        results_lists = await asyncio.gather(*tasks, return_exceptions=True)

        # 合并结果
        all_results: list[SearchResult] = []
        for results in results_lists:
            if isinstance(results, list):
                all_results.extend(results)

        return all_results

    async def _execute_search(
        self,
        sub_query: SubQuery,
        user_id: int | None,
    ) -> list[SearchResult]:
        """执行单个检索策略."""
        strategy = sub_query.strategy

        if strategy == "web_search":
            return await self._web_search(sub_query)
        elif strategy == "memory_search":
            return await self._memory_search(sub_query, user_id)
        elif strategy == "mcp_call":
            return await self._mcp_search(sub_query)
        elif strategy == "tool_call":
            return await self._tool_search(sub_query)
        else:
            # 默认使用 web 搜索
            return await self._web_search(sub_query)

    async def _web_search(self, sub_query: SubQuery) -> list[SearchResult]:
        """Web 搜索."""
        if not self.tavily_client:
            return []

        try:
            response = await self.tavily_client.search(
                query=sub_query.query,
                search_depth="advanced",
                max_results=5,
            )

            results = []
            for i, result in enumerate(response.get("results", [])):
                results.append(SearchResult(
                    source=f"web_{i}",
                    source_type="web",
                    content=result.get("content", ""),
                    url=result.get("url"),
                    title=result.get("title"),
                    relevance_score=result.get("score", 0.0),
                    metadata={"query": sub_query.query},
                ))
            return results
        except Exception as e:
            print(f"Web search error: {e}")
            return []

    async def _memory_search(
        self,
        sub_query: SubQuery,
        user_id: int | None,
    ) -> list[SearchResult]:
        """记忆检索（占位，实际实现见 MemOS 集成）."""
        # 返回空列表，实际实现由 MemoryService 提供
        return []

    async def _mcp_search(self, sub_query: SubQuery) -> list[SearchResult]:
        """MCP 工具检索（占位，实际实现见 MCP 集成）."""
        return []

    async def _tool_search(self, sub_query: SubQuery) -> list[SearchResult]:
        """内置工具检索（占位，实际实现见 Tools 集成）."""
        return []
