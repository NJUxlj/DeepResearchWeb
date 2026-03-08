"""普通聊天 Agent."""

from typing import Any, AsyncGenerator

from openai import AsyncOpenAI

from app.agents.base import BaseAgent
from app.config import settings
from app.schemas.message import Citation


class ChatAgent(BaseAgent):
    """普通聊天 Agent，使用 LLM 直接回复."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )
        self.model = settings.LLM_MODEL

    async def chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """非流式聊天."""
        messages = self._build_messages(message, history)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
        )

        content = response.choices[0].message.content or ""

        return {
            "content": content,
            "citations": [],
        }

    async def stream_chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """流式聊天."""
        messages = self._build_messages(message, history)

        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            stream=True,
        )

        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield {"type": "content", "content": delta}

        # 流结束，发送空引用
        yield {"type": "citations", "citations": []}

    def _build_messages(
        self,
        message: str,
        history: list[dict[str, str]] | None,
    ) -> list[dict[str, str]]:
        """构建消息列表."""
        messages: list[dict[str, str]] = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant. Answer user questions concisely and accurately.",
            }
        ]

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": message})

        return messages
