"""Citation 模块: 引用解析与管理."""

import re
from typing import Any

from app.schemas.message import Citation


class CitationManager:
    """引用管理器，负责解析和管理引用."""

    # 正则表达式匹配 [n] 或 [n,m,o] 格式的引用
    CITATION_PATTERN = re.compile(r"\[(\d+(?:,\d+)*)\]")

    def __init__(self, citations: list[Citation] | None = None):
        """
        初始化引用管理器.

        Args:
            citations: 引用列表
        """
        self.citations: list[Citation] = citations or []
        # 创建索引映射: citation index -> Citation object
        self._index_map: dict[int, Citation] = {
            c.index: c for c in self.citations
        }

    def add_citation(self, citation: Citation) -> None:
        """添加引用."""
        self.citations.append(citation)
        self._index_map[citation.index] = citation

    def get_citation(self, index: int) -> Citation | None:
        """根据索引获取引用."""
        return self._index_map.get(index)

    def get_citations_from_text(self, text: str) -> list[Citation]:
        """
        从文本中提取引用的 Citation 对象列表.

        Args:
            text: 包含引用标记的文本

        Returns:
            按出现顺序排列的 Citation 对象列表
        """
        found_indices: set[int] = set()
        result: list[Citation] = []

        matches = self.CITATION_PATTERN.findall(text)
        for match in matches:
            # 处理 [n,m,o] 格式
            indices = [int(x) for x in match.split(",")]
            for idx in indices:
                if idx not in found_indices and idx in self._index_map:
                    found_indices.add(idx)
                    result.append(self._index_map[idx])

        return result

    def format_citation_list(self) -> str:
        """
        格式化引用列表为可读文本.

        Returns:
            格式化后的引用列表
        """
        lines = []
        for c in sorted(self.citations, key=lambda x: x.index):
            line = f"[{c.index}] {c.title}"
            if c.url:
                line += f" - {c.url}"
            lines.append(line)
        return "\n".join(lines)

    def to_dict(self) -> list[dict[str, Any]]:
        """
        转换为字典列表.

        Returns:
            字典列表
        """
        return [
            {
                "id": c.id,
                "index": c.index,
                "url": c.url,
                "title": c.title,
                "snippet": c.snippet,
                "source_type": c.source_type,
                "favicon": c.favicon,
            }
            for c in self.citations
        ]


def parse_citations_from_report(report: str, search_results: list[dict[str, Any]]) -> list[Citation]:
    """
    从报告和搜索结果中解析并生成引用列表.

    Args:
        report: 包含引用标记的报告文本
        search_results: 搜索结果列表

    Returns:
        Citation 列表
    """
    # 提取所有引用的数字
    citation_manager = CitationManager()

    # 从搜索结果创建引用
    for i, result in enumerate(search_results[:10], start=1):
        citation = Citation(
            id=str(i),
            index=i,
            url=result.get("url", ""),
            title=result.get("title", result.get("source", "")),
            snippet=result.get("content", "")[:200],
            source_type=result.get("source_type", "web"),
        )
        citation_manager.add_citation(citation)

    return citation_manager.citations
