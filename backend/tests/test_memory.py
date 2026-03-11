"""Memory 服务和 API 测试."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.unit
class TestMemoryService:
    """Memory 服务测试."""

    @pytest.fixture
    def memory_service(self) -> Any:
        """创建 Memory 服务实例 (mocked)."""
        from app.services.memory_service import MemoryService

        service = MemoryService()
        return service

    async def test_search_memory_empty(
        self, memory_service: Any
    ) -> None:
        """测试空记忆搜索."""
        results = await memory_service.search("test query", user_id=1)
        assert isinstance(results, list)

    async def test_add_preference_memory(
        self, memory_service: Any
    ) -> None:
        """测试添加偏好记忆."""
        messages = [
            {"role": "user", "content": "I prefer Chinese"},
            {"role": "assistant", "content": "好的，我会用中文回复"},
        ]
        result = await memory_service.add_preference(
            messages=messages,
            user_id=1,
            session_id=1,
            preference_type="language",
        )
        assert result is not None
        assert isinstance(result, list)

    async def test_add_tree_memory(
        self, memory_service: Any
    ) -> None:
        """测试添加树形记忆."""
        result = await memory_service.add_tree_memory(
            content="Test tree memory",
            user_id=1,
            metadata={"category": "test"},
        )
        assert result is not None
        assert "content" in result

    async def test_process_feedback(
        self, memory_service: Any
    ) -> None:
        """测试记忆反馈处理."""
        chat_history = [
            {"role": "user", "content": "What is AI?"},
            {"role": "assistant", "content": "AI is artificial intelligence"},
        ]
        result = await memory_service.process_feedback(
            user_id=1,
            session_id=1,
            chat_history=chat_history,
            feedback_content="I prefer more detailed explanations",
        )
        assert result is not None
        assert "status" in result


@pytest.mark.unit
class TestEmbeddingService:
    """嵌入服务测试."""

    def test_jaro_similarity(self) -> None:
        """测试 Jaro 相似度计算."""
        from app.services.memory_service import EmbeddingService

        service = EmbeddingService()

        # 相同字符串
        score1 = service._jaro_similarity("hello", "hello")
        assert score1 == 1.0

        # 完全不同的字符串
        score2 = service._jaro_similarity("abc", "xyz")
        assert score2 < 1.0

        # 相似字符串
        score3 = service._jaro_similarity("hello", "hallo")
        assert 0.7 < score3 < 1.0

    def test_ngram_similarity(self) -> None:
        """测试基于 n-gram 的相似度计算."""
        from app.services.memory_service import EmbeddingService

        service = EmbeddingService()

        # 相同文本的 n-gram
        ngrams1 = service._get_ngrams("hello", 2)
        ngrams2 = service._get_ngrams("hello", 2)
        assert ngrams1 == ngrams2

        # 不同文本的 n-gram
        ngrams3 = service._get_ngrams("hello", 2)
        ngrams4 = service._get_ngrams("world", 2)
        assert ngrams3 != ngrams4

    def test_compute_similarity(self) -> None:
        """测试组合相似度计算."""
        from app.services.memory_service import EmbeddingService

        service = EmbeddingService()

        # 相同文本
        score1 = service.compute_similarity("test query", "test query")
        assert score1 == 1.0

        # 不同文本
        score2 = service.compute_similarity("hello", "goodbye")
        assert 0 <= score2 <= 1.0

    def test_extract_text_features(self) -> None:
        """测试文本特征提取."""
        from app.services.memory_service import EmbeddingService

        service = EmbeddingService()

        features = service._extract_text_features("Hello World")
        assert isinstance(features, list)
        assert len(features) == 128  # 特征向量维度


@pytest.mark.unit
class TestRerankService:
    """重排序服务测试."""

    def test_bm25_score(self) -> None:
        """测试 BM25 分数计算."""
        from app.services.memory_service import RerankService

        service = RerankService()

        # 相同查询
        score1 = service._bm25_score("test query", "test query")
        assert score1 > 0

        # 不同查询
        score2 = service._bm25_score("test", "apple banana")
        assert score2 == 0.0

    def test_rerank_empty(self) -> None:
        """测试空结果重排序."""
        from app.services.memory_service import RerankService

        service = RerankService()

        results = service.rerank("test query", [])
        assert results == []

    def test_rerank_single(self) -> None:
        """测试单结果重排序."""
        from app.services.memory_service import RerankService

        service = RerankService()

        results = service.rerank(
            "test query", [{"id": "1", "content": "test content"}]
        )
        assert len(results) == 1
        assert results[0]["id"] == "1"

    def test_rerank_multiple(self) -> None:
        """测试多结果重排序."""
        from app.services.memory_service import RerankService

        service = RerankService()

        candidates = [
            {"id": "1", "content": "unrelated content"},
            {"id": "2", "content": "test query match"},
            {"id": "3", "content": "another test query"},
        ]

        results = service.rerank("test query", candidates)
        assert len(results) == 3
        # 匹配度高的应该排在前面
        assert results[0]["rerank_score"] >= results[1]["rerank_score"]
        assert results[1]["rerank_score"] >= results[2]["rerank_score"]


@pytest.mark.api
class TestMemoryAPI:
    """Memory API 测试类."""

    async def _get_auth_token(self, client: AsyncClient) -> str:
        """获取认证 Token."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "memorytest",
                "email": "memory@example.com",
                "password": "Test123456",
            },
        )
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "memorytest", "password": "Test123456"},
        )
        return resp.json()["access_token"]

    async def test_search_memory_api(
        self, client: AsyncClient
    ) -> None:
        """测试记忆搜索 API."""
        token = await self._get_auth_token(client)

        response = await client.get(
            "/api/v1/memory/search",
            headers={"Authorization": f"Bearer {token}"},
            params={"query": "preference"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "results" in data

    async def test_add_tree_memory_api(
        self, client: AsyncClient
    ) -> None:
        """测试添加树形记忆 API."""
        token = await self._get_auth_token(client)

        response = await client.post(
            "/api/v1/memory/tree",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "content": "My project notes",
                "metadata": {"category": "work", "priority": "high"},
            },
        )
        assert response.status_code in [200, 201]

    async def test_add_preference_api(
        self, client: AsyncClient
    ) -> None:
        """测试添加偏好记忆 API."""
        token = await self._get_auth_token(client)

        response = await client.post(
            "/api/v1/memory/preference",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "session_id": 1,
                "messages": [
                    {"role": "user", "content": "I prefer dark mode"},
                    {"role": "assistant", "content": "好的，我会使用深色模式"},
                ],
                "preference_type": "ui",
            },
        )
        assert response.status_code in [200, 201]

    async def test_memory_unauthorized(
        self, client: AsyncClient
    ) -> None:
        """测试未授权访问记忆 API."""
        response = await client.get(
            "/api/v1/memory/search",
            params={"query": "test"},
        )
        assert response.status_code == 401

    async def test_feedback_api(
        self, client: AsyncClient
    ) -> None:
        """测试记忆反馈 API."""
        token = await self._get_auth_token(client)

        response = await client.post(
            "/api/v1/memory/feedback",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "session_id": 1,
                "feedback": "This memory is incorrect",
                "chat_history": [
                    {"role": "user", "content": "What is AI?"},
                    {"role": "assistant", "content": "AI is artificial intelligence"},
                ],
            },
        )
        assert response.status_code in [200, 201]
