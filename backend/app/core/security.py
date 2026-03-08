"""安全相关工具函数."""

from datetime import datetime, timedelta
from typing import Any

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext

from app.config import settings

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希."""
    # Truncate password to 72 bytes (bcrypt limit)
    return pwd_context.hash(password[:72])


def create_access_token(
    subject: int | str,
    expires_delta: timedelta | None = None,
) -> tuple[str, int]:
    """
    创建 JWT 访问令牌.

    Returns:
        tuple: (token, expires_in_seconds)
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        expires_in = int(expires_delta.total_seconds())
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    to_encode: dict[str, Any] = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt, expires_in


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    解码并验证 JWT 令牌.

    Returns:
        解码后的 payload，如果验证失败返回 None
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except InvalidTokenError:
        return None
