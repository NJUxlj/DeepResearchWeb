"""聊天和会话 API 测试."""

import pytest
from httpx import AsyncClient


@pytest.mark.api
class TestSessionAPI:
    """会话 API 测试类."""

    async def _get_auth_token(self, client: AsyncClient) -> str:
        """获取认证 Token."""
        # 注册
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "sessiontest",
                "email": "session@example.com",
                "password": "Test123456",
            },
        )
        # 登录
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "sessiontest", "password": "Test123456"},
        )
        return resp.json()["access_token"]

    async def test_create_session(self, client: AsyncClient) -> None:
        """测试创建会话."""
        token = await self._get_auth_token(client)

        response = await client.post(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Test Session", "mode": "chat"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Session"
        assert data["mode"] == "chat"

    async def test_create_research_session(self, client: AsyncClient) -> None:
        """测试创建研究模式会话."""
        token = await self._get_auth_token(client)

        response = await client.post(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Research Session", "mode": "research"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["mode"] == "research"

    async def test_list_sessions(self, client: AsyncClient) -> None:
        """测试获取会话列表."""
        token = await self._get_auth_token(client)

        # 创建会话
        await client.post(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Session 1", "mode": "chat"},
        )

        # 获取列表
        response = await client.get(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    async def test_list_sessions_by_mode(self, client: AsyncClient) -> None:
        """测试按模式过滤会话."""
        token = await self._get_auth_token(client)

        # 创建不同模式的会话
        await client.post(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Chat Session", "mode": "chat"},
        )
        await client.post(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Research Session", "mode": "research"},
        )

        # 按 chat 模式过滤
        response = await client.get(
            "/api/v1/sessions?mode=chat",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        # 所有返回的会话都应该是 chat 模式
        for item in data["items"]:
            assert item["mode"] == "chat"

    async def test_get_session_detail(self, client: AsyncClient) -> None:
        """测试获取会话详情."""
        token = await self._get_auth_token(client)

        # 创建会话
        create_resp = await client.post(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Detail Test", "mode": "chat"},
        )
        session_id = create_resp.json()["id"]

        # 获取详情
        response = await client.get(
            f"/api/v1/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Detail Test"

    async def test_get_session_not_found(self, client: AsyncClient) -> None:
        """测试获取不存在的会话."""
        token = await self._get_auth_token(client)

        response = await client.get(
            "/api/v1/sessions/99999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    async def test_update_session(self, client: AsyncClient) -> None:
        """测试更新会话."""
        token = await self._get_auth_token(client)

        # 创建会话
        create_resp = await client.post(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Original Title", "mode": "chat"},
        )
        session_id = create_resp.json()["id"]

        # 更新会话
        response = await client.put(
            f"/api/v1/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Updated Title"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    async def test_delete_session(self, client: AsyncClient) -> None:
        """测试删除会话."""
        token = await self._get_auth_token(client)

        # 创建会话
        create_resp = await client.post(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "To Delete", "mode": "chat"},
        )
        session_id = create_resp.json()["id"]

        # 删除
        response = await client.delete(
            f"/api/v1/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 204

        # 验证已删除
        get_resp = await client.get(
            f"/api/v1/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_resp.status_code == 404

    async def test_delete_other_user_session(self, client: AsyncClient) -> None:
        """测试删除其他用户的会话."""
        token1 = await self._get_auth_token(client)

        # 用户1创建会话
        create_resp = await client.post(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {token1}"},
            json={"title": "User1 Session", "mode": "chat"},
        )
        session_id = create_resp.json()["id"]

        # 注册并登录用户2
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "user2",
                "email": "user2@example.com",
                "password": "Test123456",
            },
        )
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "user2", "password": "Test123456"},
        )
        token2 = resp.json()["access_token"]

        # 用户2尝试删除用户1的会话
        response = await client.delete(
            f"/api/v1/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert response.status_code == 404


@pytest.mark.api
class TestMessageAPI:
    """消息 API 测试类."""

    async def _get_auth_token(self, client: AsyncClient) -> tuple[str, int]:
        """获取认证 Token 和用户ID."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "msgetest",
                "email": "msg@example.com",
                "password": "Test123456",
            },
        )
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "msgetest", "password": "Test123456"},
        )
        token = resp.json()["access_token"]

        # 获取用户信息
        me_resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        user_id = me_resp.json()["id"]

        return token, user_id

    async def test_create_message(self, client: AsyncClient) -> None:
        """测试创建消息."""
        token, _ = await self._get_auth_token(client)

        # 创建会话
        session_resp = await client.post(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Message Test", "mode": "chat"},
        )
        session_id = session_resp.json()["id"]

        # 创建消息
        response = await client.post(
            "/api/v1/messages",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "session_id": session_id,
                "role": "user",
                "content": "Hello, world!",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Hello, world!"
        assert data["role"] == "user"

    async def test_get_session_messages(self, client: AsyncClient) -> None:
        """测试获取会话消息列表."""
        token, _ = await self._get_auth_token(client)

        # 创建会话
        session_resp = await client.post(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Messages List Test", "mode": "chat"},
        )
        session_id = session_resp.json()["id"]

        # 创建消息
        await client.post(
            "/api/v1/messages",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "session_id": session_id,
                "role": "user",
                "content": "Message 1",
            },
        )
        await client.post(
            "/api/v1/messages",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "session_id": session_id,
                "role": "assistant",
                "content": "Message 2",
            },
        )

        # 获取消息列表
        response = await client.get(
            f"/api/v1/messages/by-session/{session_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    async def test_update_message(self, client: AsyncClient) -> None:
        """测试更新消息."""
        token, _ = await self._get_auth_token(client)

        # 创建会话
        session_resp = await client.post(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Update Test", "mode": "chat"},
        )
        session_id = session_resp.json()["id"]

        # 创建消息
        msg_resp = await client.post(
            "/api/v1/messages",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "session_id": session_id,
                "role": "user",
                "content": "Original content",
            },
        )
        message_id = msg_resp.json()["id"]

        # 更新消息
        response = await client.put(
            f"/api/v1/messages/{message_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"content": "Updated content"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated content"

    async def test_delete_message(self, client: AsyncClient) -> None:
        """测试删除消息."""
        token, _ = await self._get_auth_token(client)

        # 创建会话
        session_resp = await client.post(
            "/api/v1/sessions",
            headers={"Authorization": f"Bearer {token}"},
            json={"title": "Delete Test", "mode": "chat"},
        )
        session_id = session_resp.json()["id"]

        # 创建消息
        msg_resp = await client.post(
            "/api/v1/messages",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "session_id": session_id,
                "role": "user",
                "content": "To delete",
            },
        )
        message_id = msg_resp.json()["id"]

        # 删除消息
        response = await client.delete(
            f"/api/v1/messages/{message_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 204
