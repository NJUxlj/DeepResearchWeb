"""Agent 基类."""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator


class BaseAgent(ABC):
    """Agent 基类."""

    @abstractmethod
    async def chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """
        非流式聊天.

        Args:
            message: 用户消息
            history: 聊天历史

        Returns:
            包含 content 和 citations 的字典
        """
        pass

    @abstractmethod
    async def stream_chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        流式聊天.

        Args:
            message: 用户消息
            history: 聊天历史

        Yields:
            包含 type 和内容的字典:
            - {"type": "content", "content": "..."}
            - {"type": "citations", "citations": [...]}
        """
        pass
