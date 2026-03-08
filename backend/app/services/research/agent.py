"""Research Agent 主逻辑."""

from typing import Any, AsyncGenerator, Callable

from app.schemas.research import (
    ResearchConfig,
    ResearchIteration,
    ResearchResult,
    SubQuery,
)
from app.services.research.planner import ResearchPlanner
from app.services.research.searcher import ResearchSearcher
from app.services.research.synthesizer import ResearchSynthesizer


class ResearchAgent:
    """深度研究 Agent 核心逻辑."""

    def __init__(self, config: ResearchConfig | None = None):
        self.config = config or ResearchConfig()
        self.planner = ResearchPlanner()
        self.searcher = ResearchSearcher()
        self.synthesizer = ResearchSynthesizer()

    async def research(
        self,
        query: str,
        user_id: int | None = None,
        on_event: Callable[[str, dict[str, Any]], Any] | None = None,
    ) -> ResearchResult:
        """
        执行深度研究.

        Args:
            query: 用户查询
            user_id: 用户 ID
            on_event: 事件回调函数

        Returns:
            研究结果
        """
        iterations: list[ResearchIteration] = []

        # 1. Plan: 问题分解
        if on_event:
            await on_event("plan", {"status": "started", "query": query})

        plan_result = await self.planner.plan(query)

        if plan_result.get("needs_clarification"):
            if on_event:
                await on_event("clarify", {
                    "question": plan_result.get("clarification_question")
                })
            raise ValueError(f"Needs clarification: {plan_result.get('clarification_question')}")

        sub_queries: list[SubQuery] = plan_result.get("sub_queries", [])

        if on_event:
            await on_event("plan", {"status": "completed", "sub_queries": len(sub_queries)})

        # 2-4. Search + Synthesize 迭代
        previous_synthesis = None

        for iteration in range(self.config.max_iterations):
            if on_event:
                await on_event("search", {
                    "iteration": iteration + 1,
                    "status": "started",
                })

            # Search: 多源检索
            search_results = await self.searcher.search(sub_queries, user_id)

            if on_event:
                await on_event("search", {
                    "iteration": iteration + 1,
                    "status": "completed",
                    "results_count": len(search_results),
                })

            if not search_results:
                break

            # Synthesize: 综合判断
            if on_event:
                await on_event("synthesis", {
                    "iteration": iteration + 1,
                    "status": "started",
                })

            synthesis_result = await self.synthesizer.synthesize(
                query=query,
                search_results=search_results,
                iteration=iteration + 1,
                previous_synthesis=previous_synthesis,
            )

            needs_more = synthesis_result.get("needs_more_info", False)

            iteration_data = ResearchIteration(
                iteration=iteration + 1,
                sub_queries=sub_queries,
                search_results=search_results,
                synthesis=synthesis_result.get("synthesis", ""),
                needs_more_info=needs_more,
            )
            iterations.append(iteration_data)

            if on_event:
                await on_event("synthesis", {
                    "iteration": iteration + 1,
                    "status": "completed",
                    "needs_more_info": needs_more,
                    "confidence": synthesis_result.get("confidence", 0),
                })

            # 检查是否继续迭代
            if not needs_more or iteration >= self.config.max_iterations - 1:
                break

            # 生成新的子查询
            additional_queries = synthesis_result.get("additional_queries", [])
            if additional_queries:
                sub_queries = [
                    SubQuery(
                        id=f"{iteration+1}_{i}",
                        query=q,
                        strategy="web_search",
                        priority=3,
                    )
                    for i, q in enumerate(additional_queries[:3])
                ]
            else:
                break

            previous_synthesis = synthesis_result.get("synthesis")

        # 5. Report: 生成报告
        if on_event:
            await on_event("report", {"status": "started"})

        report_result = await self.synthesizer.generate_report(query, [
            {
                "search_results": it.search_results,
                "synthesis": it.synthesis,
            }
            for it in iterations
        ])

        if on_event:
            await on_event("report", {"status": "completed"})

        from datetime import datetime

        return ResearchResult(
            query=query,
            iterations=iterations,
            final_report=report_result["report"],
            citations=report_result["citations"],
            total_sources=sum(len(it.search_results) for it in iterations),
            completed_at=datetime.utcnow(),
        )

    async def stream_research(
        self,
        query: str,
        user_id: int | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """流式研究，生成事件流."""

        # Plan
        yield {"event": "plan", "data": {"status": "started"}}
        plan_result = await self.planner.plan(query)
        yield {"event": "plan", "data": {"status": "completed"}}

        if plan_result.get("needs_clarification"):
            yield {
                "event": "clarify",
                "data": {"question": plan_result.get("clarification_question")}
            }
            return

        sub_queries = plan_result.get("sub_queries", [])

        # Search + Synthesize 迭代
        for iteration in range(self.config.max_iterations):
            yield {"event": "search", "data": {"iteration": iteration + 1, "status": "started"}}

            search_results = await self.searcher.search(sub_queries, user_id)

            yield {
                "event": "search",
                "data": {"iteration": iteration + 1, "results_count": len(search_results)}
            }

            if not search_results:
                break

            yield {"event": "synthesis", "data": {"iteration": iteration + 1, "status": "started"}}

            synthesis_result = await self.synthesizer.synthesize(
                query=query,
                search_results=search_results,
                iteration=iteration + 1,
            )

            yield {
                "event": "synthesis",
                "data": {
                    "iteration": iteration + 1,
                    "needs_more_info": synthesis_result.get("needs_more_info", False),
                }
            }

            if not synthesis_result.get("needs_more_info", False):
                break

        # Report
        yield {"event": "report", "data": {"status": "generating"}}

        # 简化：返回最终结果
        yield {"event": "complete", "data": {"status": "done"}}
