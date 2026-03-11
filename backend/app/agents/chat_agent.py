"""普通聊天 Agent."""

import logging
from typing import Any, AsyncGenerator

from openai import AsyncOpenAI

from app.agents.base import BaseAgent
from app.config import settings

logger = logging.getLogger(__name__)


class ChatAgent(BaseAgent):
    """普通聊天 Agent，使用 LLM 直接回复."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )
        self.model = settings.LLM_MODEL
        # 检查是否是 MiniMax 模型
        self.is_minimax = "minimax" in self.model.lower()
        logger.info(f"ChatAgent initialized with model: {self.model}, is_minimax: {self.is_minimax}")

    async def chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        """非流式聊天."""
        messages = self._build_messages(message, history)

        # 构建请求参数
        extra_body = {}
        if self.is_minimax:
            extra_body["thinking_type"] = "continuous"

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            extra_body=extra_body if extra_body else None,
        )

        msg = response.choices[0].message
        raw_content = msg.content or ""

        # 从内容中提取思维链（处理非流式响应）
        thinking, content = self._extract_thinking_from_content(raw_content)

        if thinking:
            logger.info(f"Extracted thinking: {thinking[:100]}...")

        return {
            "content": content,
            "thinking": thinking,
            "citations": [],
        }

    def _extract_thinking_from_content(self, raw_content: str) -> tuple[str, str]:
        """从内容中提取思维链。"""
        if not raw_content:
            return "", ""

        import re
        thinking_pattern = r"<think>(.*?)</think>"
        thinking_matches = re.findall(thinking_pattern, raw_content, re.DOTALL)

        if thinking_matches:
            thinking = "".join(thinking_matches)
            content_without_thinking = re.sub(thinking_pattern, "", raw_content, flags=re.DOTALL).strip()
            return thinking, content_without_thinking

        return "", raw_content

    async def stream_chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """流式聊天."""
        messages = self._build_messages(message, history)

        # 构建请求参数
        extra_body = {}
        if self.is_minimax:
            extra_body["thinking_type"] = "continuous"

        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            stream=True,
            extra_body=extra_body if extra_body else None,
        )

        # 状态机变量
        in_thinking = False
        thinking_buffer = ""

        async for chunk in stream:
            delta = chunk.choices[0].delta

            raw_delta_content = delta.content or ""

            if not raw_delta_content:
                continue

            if not in_thinking:
                # 查找开始标签
                start_tag = "<think>"
                idx = raw_delta_content.find(start_tag)
                if idx != -1:
                    # 输出开始标签之前的内容
                    if idx > 0:
                        yield {"type": "content", "content": raw_delta_content[:idx]}
                    # 进入思考模式
                    in_thinking = True
                    thinking_buffer = raw_delta_content[idx + len(start_tag):]
                    # 立即发送当前已累积的思考内容
                    if thinking_buffer:
                        yield {"type": "thinking", "content": thinking_buffer}
                        thinking_buffer = ""
                else:
                    # 没有开始标签，全部作为内容
                    yield {"type": "content", "content": raw_delta_content}
            else:
                # 在思考模式中，查找结束标签
                end_tag = "</think>"
                idx = raw_delta_content.find(end_tag)
                if idx != -1:
                    # 获取思考内容并发送
                    thinking_buffer += raw_delta_content[:idx]
                    if thinking_buffer:
                        yield {"type": "thinking", "content": thinking_buffer}
                        thinking_buffer = ""
                    in_thinking = False
                    # 输出结束标签之后的内容
                    remaining = raw_delta_content[idx + len(end_tag):]
                    if remaining:
                        yield {"type": "content", "content": remaining}
                else:
                    # 还没找到结束标签，立即发送新到的思考内容
                    yield {"type": "thinking", "content": raw_delta_content}

        # 处理剩余的思考内容（如果标签未闭合）
        if in_thinking and thinking_buffer:
            yield {"type": "thinking", "content": thinking_buffer}

        logger.info(f"Stream finished")
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
