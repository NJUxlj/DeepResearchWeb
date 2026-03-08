"""Synthesizer: 综合检索结果并判断信息充分性."""

import json
from typing import Any

from openai import AsyncOpenAI

from app.config import settings
from app.schemas.message import Citation
from app.schemas.research import SearchResult


SYNTHESIZER_SYSTEM_PROMPT = """You are a research synthesizer. Your task is to:
1. Synthesize the search results into a coherent analysis
2. Determine if the information is sufficient to answer the original query
3. If not, identify what additional information is needed

Output in JSON format:
{
  "synthesis": "Your analysis and synthesis of the search results",
  "needs_more_info": false,
  "additional_queries": ["query1", "query2"],
  "confidence": 0.85
}

confidence: 0-1 score indicating how confident you are that the current information is sufficient.
"""


class ResearchSynthesizer:
    """研究综合器."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )
        self.model = settings.LLM_MODEL

    async def synthesize(
        self,
        query: str,
        search_results: list[SearchResult],
        iteration: int,
        previous_synthesis: str | None = None,
    ) -> dict[str, Any]:
        """
        综合检索结果.

        Returns:
            {
                "synthesis": str,
                "needs_more_info": bool,
                "additional_queries": list[str],
                "confidence": float
            }
        """
        # 构建搜索结果文本
        results_text = "\n\n".join([
            f"Source {i+1} ({r.source_type}):\n{r.content}"
            for i, r in enumerate(search_results)
        ])

        context = f"""Original Query: {query}

Search Results:
{results_text}

Iteration: {iteration}
"""
        if previous_synthesis:
            context += f"\nPrevious Synthesis:\n{previous_synthesis}"

        messages = [
            {"role": "system", "content": SYNTHESIZER_SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    async def generate_report(
        self,
        query: str,
        iterations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        生成最终研究报告.

        Returns:
            {
                "report": str,
                "citations": list[Citation]
            }
        """
        # 收集所有搜索结果
        all_results: list[SearchResult] = []
        for it in iterations:
            all_results.extend(it.get("search_results", []))

        # 去重并按相关性排序
        seen_sources = set()
        unique_results: list[SearchResult] = []
        for r in sorted(all_results, key=lambda x: x.relevance_score, reverse=True):
            key = (r.source_type, r.url or r.source)
            if key not in seen_sources:
                seen_sources.add(key)
                unique_results.append(r)

        # 生成报告
        results_text = "\n\n".join([
            f"[{i+1}] {r.title or r.source}\n{r.content}"
            for i, r in enumerate(unique_results[:10])  # 取前 10 个
        ])

        prompt = f"""Based on the research results below, write a comprehensive report answering the query: {query}

Research Results:
{results_text}

Requirements:
1. Write in a clear, structured format with sections if appropriate
2. Include inline citations in the format [n] to reference sources
3. Be factual and cite specific data points
4. Acknowledge any limitations or uncertainties
"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a research report writer."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )

        report = response.choices[0].message.content or ""

        # 生成引用
        citations = []
        for i, r in enumerate(unique_results[:10]):
            citations.append(Citation(
                id=str(i + 1),
                index=i + 1,
                url=r.url or "",
                title=r.title or r.source,
                snippet=r.content[:200],
                source_type=r.source_type,
            ))

        return {
            "report": report,
            "citations": citations,
        }
