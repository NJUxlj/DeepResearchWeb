"""Planner: 问题分解与规划."""

import json
from typing import Any

from openai import AsyncOpenAI

from app.config import settings
from app.schemas.research import SubQuery


PLANNER_SYSTEM_PROMPT = """You are a research planner. Your task is to break down a complex user query into sub-queries that can be independently researched.

For each sub-query, specify:
- query: The specific search query
- strategy: One of [web_search, memory_search, mcp_call, tool_call]
- target: Optional specific target (e.g., specific MCP server or tool name)
- priority: 1-5 (higher = more important)

Output in JSON format:
{
  "needs_clarification": false,
  "clarification_question": null,
  "sub_queries": [
    {
      "id": "1",
      "query": "specific sub-query",
      "strategy": "web_search",
      "target": null,
      "priority": 5
    }
  ]
}

If the query is ambiguous or needs more context, set needs_clarification to true and provide a clarification_question.
"""


class ResearchPlanner:
    """研究规划器."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )
        self.model = settings.LLM_MODEL

    async def plan(
        self,
        query: str,
        context: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """
        分析查询并生成研究计划.

        Returns:
            {
                "needs_clarification": bool,
                "clarification_question": str | None,
                "sub_queries": list[SubQuery]
            }
        """
        messages = [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": f"User query: {query}"},
        ]

        # 添加上下文（如果有）
        if context:
            for msg in context:
                messages.append(msg)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        content = response.choices[0].message.content or "{}"
        result = json.loads(content)

        # 转换为 SubQuery 对象
        if result.get("sub_queries"):
            result["sub_queries"] = [SubQuery(**sq) for sq in result["sub_queries"]]

        return result
