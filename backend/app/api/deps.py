"""依赖注入."""

from typing import Annotated, AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import AuthenticationException
from app.db.database import get_db as _get_db
from app.models.user import User

# HTTP Bearer 认证
http_bearer = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话依赖."""
    async for session in _get_db():
        yield session


# 类型别名
DBDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DBDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer)],
) -> User:
    """
    获取当前登录用户.

    从 HTTP Bearer Token 中解析用户信息.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str | None = payload.get("sub")
        token_type: str = payload.get("type", "access")

        if user_id is None:
            raise AuthenticationException("Invalid token: missing user id")

        if token_type != "access":
            raise AuthenticationException("Invalid token type")

    except (ExpiredSignatureError, InvalidTokenError):
        raise AuthenticationException("Invalid or expired token")

    # 查询用户
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise AuthenticationException("User not found")

    if not user.is_active:
        raise AuthenticationException("User is inactive")

    return user


# 当前用户依赖类型
CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_current_active_superuser(
    current_user: CurrentUserDep,
) -> User:
    """获取当前超级管理员用户."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


SuperuserDep = Annotated[User, Depends(get_current_active_superuser)]
