"""DeepResearch Agent 实现."""

from typing import Any, AsyncGenerator

from app.agents.base import BaseAgent
from app.schemas.research import ResearchConfig
from app.services.research.agent import ResearchAgent as ResearchAgentCore


class ResearchAgent(BaseAgent):
    """深度研究 Agent，继承自 BaseAgent."""

    def __init__(self, config: ResearchConfig | None = None):
        self.config = config or ResearchConfig()
        self._core = ResearchAgentCore(self.config)

    async def chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """
        非流式聊天（兼容 BaseAgent 接口）.

        Args:
            message: 用户消息
            history: 聊天历史

        Returns:
            包含 content 和 citations 的字典
        """
        result = await self._core.research(message)
        return {
            "content": result.final_report,
            "citations": result.citations,
        }

    async def stream_chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        流式聊天（兼容 BaseAgent 接口）.

        Args:
            message: 用户消息
            history: 聊天历史

        Yields:
            包含 type 和内容的字典:
            - {"type": "content", "content": "..."}
            - {"type": "citations", "citations": [...]}
        """
        # 用于收集完整结果
        final_content = ""
        final_citations = []

        async for event in self._core.stream_research(message):
            event_type = event.get("event")
            data = event.get("data", {})

            if event_type == "report":
                # 报告生成中，收集内容
                pass
            elif event_type == "complete":
                # 完成，获取最终结果
                pass
            else:
                # 其他事件，转发为 content 类型
                yield {"type": "event", "event": event_type, "data": data}

        # 由于 stream_research 不返回完整内容，我们需要获取完整结果
        result = await self._core.research(message)
        yield {"type": "content", "content": result.final_report}
        yield {"type": "citations", "citations": result.citations}
