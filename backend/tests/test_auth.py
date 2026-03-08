"""认证 API 测试."""

import pytest
from httpx import AsyncClient


@pytest.mark.api
class TestAuthAPI:
    """认证 API 测试类."""

    async def test_register_success(self, client: AsyncClient) -> None:
        """测试注册成功."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "Test123456",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert "id" in data

    async def test_register_duplicate_username(self, client: AsyncClient) -> None:
        """测试重复用户名."""
        # 先注册一个用户
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "dupuser",
                "email": "dup1@example.com",
                "password": "Test123456",
            },
        )

        # 再尝试注册相同用户名
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "dupuser",
                "email": "dup2@example.com",
                "password": "Test123456",
            },
        )
        assert response.status_code == 409

    async def test_register_duplicate_email(self, client: AsyncClient) -> None:
        """测试重复邮箱."""
        # 先注册一个用户
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "user1",
                "email": "same@example.com",
                "password": "Test123456",
            },
        )

        # 再尝试注册相同邮箱
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "user2",
                "email": "same@example.com",
                "password": "Test123456",
            },
        )
        assert response.status_code == 409

    async def test_register_invalid_email(self, client: AsyncClient) -> None:
        """测试无效邮箱格式."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "validuser",
                "email": "not-an-email",
                "password": "Test123456",
            },
        )
        assert response.status_code == 422

    async def test_register_short_password(self, client: AsyncClient) -> None:
        """测试密码过短."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "short",
            },
        )
        assert response.status_code == 422

    async def test_login_success(self, client: AsyncClient, mock_user_data: dict) -> None:
        """测试登录成功."""
        # 先注册
        await client.post("/api/v1/auth/register", json=mock_user_data)

        # 登录
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": mock_user_data["username"],
                "password": mock_user_data["password"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(
        self, client: AsyncClient, mock_user_data: dict
    ) -> None:
        """测试密码错误."""
        # 先注册
        await client.post("/api/v1/auth/register", json=mock_user_data)

        # 错误密码登录
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": mock_user_data["username"],
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient) -> None:
        """测试不存在的用户登录."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "Test123456",
            },
        )
        assert response.status_code == 401

    async def test_get_me_unauthorized(self, client: AsyncClient) -> None:
        """测试未授权访问."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_get_me_authorized(
        self, client: AsyncClient, mock_user_data: dict
    ) -> None:
        """测试已授权访问."""
        # 注册并登录
        await client.post("/api/v1/auth/register", json=mock_user_data)
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={
                "username": mock_user_data["username"],
                "password": mock_user_data["password"],
            },
        )
        token = login_resp.json()["access_token"]

        # 访问受保护端点
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == mock_user_data["username"]

    async def test_update_me(self, client: AsyncClient, mock_user_data: dict) -> None:
        """测试更新用户信息."""
        # 注册并登录
        await client.post("/api/v1/auth/register", json=mock_user_data)
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={
                "username": mock_user_data["username"],
                "password": mock_user_data["password"],
            },
        )
        token = login_resp.json()["access_token"]

        # 更新邮箱
        response = await client.put(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"email": "updated@example.com"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "updated@example.com"

    async def test_update_password(self, client: AsyncClient, mock_user_data: dict) -> None:
        """测试更新密码."""
        # 注册并登录
        await client.post("/api/v1/auth/register", json=mock_user_data)
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={
                "username": mock_user_data["username"],
                "password": mock_user_data["password"],
            },
        )
        token = login_resp.json()["access_token"]

        # 更新密码
        new_password = "NewTest123456"
        response = await client.put(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            json={"password": new_password},
        )
        assert response.status_code == 200

        # 使用新密码登录
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={
                "username": mock_user_data["username"],
                "password": new_password,
            },
        )
        assert login_resp.status_code == 200

    async def test_invalid_token(self, client: AsyncClient) -> None:
        """测试无效 Token."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401

    async def test_expired_token_format(self, client: AsyncClient) -> None:
        """测试错误格式的 Token."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "NotBearer token"},
        )
        assert response.status_code == 401
