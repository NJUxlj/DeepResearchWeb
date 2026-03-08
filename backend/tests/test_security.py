"""安全工具测试."""

import pytest
from jose import jwt

from app.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


class TestSecurity:
    """安全功能测试."""

    def test_password_hash(self) -> None:
        """测试密码哈希."""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_create_access_token(self) -> None:
        """测试创建 JWT Token."""
        user_id = 123
        token, expires_in = create_access_token(user_id)

        assert token is not None
        assert isinstance(expires_in, int)
        assert expires_in > 0

    def test_decode_access_token(self) -> None:
        """测试解码 JWT Token."""
        user_id = 123
        token, _ = create_access_token(user_id)

        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["type"] == "access"

    def test_decode_invalid_token(self) -> None:
        """测试解码无效 Token."""
        payload = decode_access_token("invalid.token.here")
        assert payload is None

    def test_decode_expired_token(self) -> None:
        """测试解码过期 Token."""
        from datetime import datetime, timedelta

        # 创建一个已过期的 token
        expire = datetime.utcnow() - timedelta(minutes=30)
        to_encode = {
            "exp": expire,
            "sub": "123",
            "type": "access",
            "iat": datetime.utcnow(),
        }
        expired_token = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

        payload = decode_access_token(expired_token)
        assert payload is None

    def test_password_hash_uniqueness(self) -> None:
        """测试相同密码生成不同哈希."""
        password = "samepassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # bcrypt 每次生成不同的盐值
        assert hash1 != hash2
        # 但两个都能验证通过
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_verify_password_with_wrong_type(self) -> None:
        """测试错误类型的密码验证."""
        password = "testpassword"
        hashed = get_password_hash(password)

        # 测试各种错误输入
        assert verify_password(None, hashed) is False
        assert verify_password(123, hashed) is False
        assert verify_password("", hashed) is False
