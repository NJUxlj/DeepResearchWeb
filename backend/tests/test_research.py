"""Research 服务和 API 测试."""

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.schemas.research import SearchResult, SubQuery
from app.services.research.planner import ResearchPlanner
from app.services.research.searcher import ResearchSearcher
from app.services.research.synthesizer import ResearchSynthesizer


@pytest.mark.unit
class TestResearchPlanner:
    """Planner 测试."""

    @pytest.fixture
    def planner(self) -> ResearchPlanner:
        return ResearchPlanner()

    @patch("app.services.research.planner.AsyncOpenAI")
    async def test_plan_simple_query(
        self, mock_openai: MagicMock, planner: ResearchPlanner
    ) -> None:
        """测试简单查询规划."""
        # Mock OpenAI 响应
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps(
                        {
                            "needs_clarification": False,
                            "clarification_question": None,
                            "sub_queries": [
                                {
                                    "id": "1",
                                    "query": "test query",
                                    "strategy": "web_search",
                                    "target": None,
                                    "priority": 5,
                                }
                            ],
                        }
                    )
                )
            )
        ]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        result = await planner.plan("What is AI?")

        assert result["needs_clarification"] is False
        assert len(result["sub_queries"]) == 1
        assert isinstance(result["sub_queries"][0], SubQuery)

    @patch("app.services.research.planner.AsyncOpenAI")
    async def test_plan_needs_clarification(
        self, mock_openai: MagicMock, planner: ResearchPlanner
    ) -> None:
        """测试需要澄清的查询."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps(
                        {
                            "needs_clarification": True,
                            "clarification_question": "What specific aspect?",
                            "sub_queries": [],
                        }
                    )
                )
            )
        ]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        result = await planner.plan("Tell me about it")

        assert result["needs_clarification"] is True
        assert "clarification_question" in result


@pytest.mark.unit
class TestResearchSearcher:
    """Searcher 测试."""

    @pytest.fixture
    def searcher(self) -> ResearchSearcher:
        return ResearchSearcher()

    async def test_search_empty_subqueries(
        self, searcher: ResearchSearcher
    ) -> None:
        """测试空子查询列表."""
        results = await searcher.search([], user_id=1)
        assert results == []

    @patch("app.services.research.searcher.AsyncTavilyClient")
    async def test_web_search_success(
        self, mock_tavily: MagicMock, searcher: ResearchSearcher
    ) -> None:
        """测试 Web 搜索成功."""
        # Mock Tavily
        mock_client = MagicMock()
        mock_client.search = AsyncMock(
            return_value={
                "results": [
                    {
                        "content": "Result 1",
                        "url": "http://example.com/1",
                        "title": "Title 1",
                        "score": 0.9,
                    },
                    {
                        "content": "Result 2",
                        "url": "http://example.com/2",
                        "title": "Title 2",
                        "score": 0.8,
                    },
                ]
            }
        )
        mock_tavily.return_value = mock_client

        sub_queries = [
            SubQuery(id="1", query="test", strategy="web_search", priority=5)
        ]
        results = await searcher.search(sub_queries, user_id=1)

        assert len(results) == 2
        assert results[0].source_type == "web"


@pytest.mark.unit
class TestResearchSynthesizer:
    """Synthesizer 测试."""

    @pytest.fixture
    def synthesizer(self) -> ResearchSynthesizer:
        return ResearchSynthesizer()

    @patch("app.services.research.synthesizer.AsyncOpenAI")
    async def test_synthesize_sufficient_info(
        self, mock_openai: MagicMock, synthesizer: ResearchSynthesizer
    ) -> None:
        """测试信息充分的情况."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps(
                        {
                            "synthesis": "AI is...",
                            "needs_more_info": False,
                            "additional_queries": [],
                            "confidence": 0.9,
                        }
                    )
                )
            )
        ]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        search_results = [
            SearchResult(
                source="web_1",
                source_type="web",
                content="AI content",
                relevance_score=0.9,
            )
        ]

        result = await synthesizer.synthesize(
            query="What is AI?",
            search_results=search_results,
            iteration=1,
        )

        assert result["needs_more_info"] is False
        assert "synthesis" in result


@pytest.mark.api
class TestResearchAPI:
    """Research API 测试类."""

    async def _get_auth_token(self, client: AsyncClient) -> str:
        """获取认证 Token."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "researchtest",
                "email": "research@example.com",
                "password": "Test123456",
            },
        )
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "researchtest", "password": "Test123456"},
        )
        return resp.json()["access_token"]

    @patch("app.services.research.agent.AsyncOpenAI")
    async def test_create_research_task(
        self, mock_openai: MagicMock, client: AsyncClient
    ) -> None:
        """测试创建研究任务."""
        token = await self._get_auth_token(client)

        # Mock the response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content=json.dumps(
                        {
                            "needs_clarification": False,
                            "clarification_question": None,
                            "sub_queries": [
                                {
                                    "id": "1",
                                    "query": "artificial intelligence",
                                    "strategy": "web_search",
                                    "target": None,
                                    "priority": 5,
                                }
                            ],
                        }
                    )
                )
            )
        ]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.return_value = mock_client

        response = await client.post(
            "/api/v1/research/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "query": "What is artificial intelligence?",
                "config": {
                    "max_iterations": 3,
                    "search_depth": "standard",
                    "include_web": True,
                },
            },
        )
        # 可能返回 201 或其他状态，取决于实现
        assert response.status_code in [201, 202, 200]

    async def test_get_research_tasks(
        self, client: AsyncClient
    ) -> None:
        """测试获取研究任务列表."""
        token = await self._get_auth_token(client)

        response = await client.get(
            "/api/v1/research/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    async def test_get_research_task_detail(
        self, client: AsyncClient
    ) -> None:
        """测试获取研究任务详情."""
        token = await self._get_auth_token(client)

        response = await client.get(
            "/api/v1/research/tasks/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        # 可能返回 404 如果任务不存在
        assert response.status_code in [200, 404]


@pytest.mark.unit
class TestCitationModule:
    """Citation 模块测试."""

    def test_citation_format(self) -> None:
        """测试引用格式化."""
        from app.services.research.citation import CitationManager

        manager = CitationManager()

        # 测试添加引用
        manager.add_citation("source1", "https://example.com", "Example Title")

        citations = manager.get_citations()
        assert len(citations) == 1
        assert citations[0]["source_id"] == "source1"

    def test_citation_unique_sources(self) -> None:
        """测试引用源唯一性."""
        from app.services.research.citation import CitationManager

        manager = CitationManager()

        # 添加相同源多次
        manager.add_citation("source1", "https://example.com", "Example")
        manager.add_citation("source1", "https://example.com", "Example")

        citations = manager.get_citations()
        assert len(citations) == 1

    def test_citation_clear(self) -> None:
        """测试清除引用."""
        from app.services.research.citation import CitationManager

        manager = CitationManager()

        manager.add_citation("source1", "https://example.com", "Example")
        manager.clear()

        assert len(manager.get_citations()) == 0
