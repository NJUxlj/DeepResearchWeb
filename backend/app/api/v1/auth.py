"""认证相关 API 端点."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUserDep, DBDep
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.user import (
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
)
async def register(db: DBDep, data: UserCreate) -> User:
    """
    注册新用户.

    - 用户名 3-50 字符，唯一
    - 邮箱格式验证，唯一
    - 密码至少 8 位，包含大小写字母和数字
    """
    # 检查用户名是否已存在
    result = await db.execute(
        select(User).where(User.username == data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )

    # 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # 创建用户
    user = User(
        username=data.username,
        email=str(data.email),
        hashed_password=get_password_hash(data.password),
    )

    db.add(user)

    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    return user


@router.post(
    "/login",
    response_model=Token,
    summary="用户登录",
)
async def login(db: DBDep, data: UserLogin) -> Token:
    """
    用户登录，返回 JWT Token.

    - 支持用户名登录
    - Token 有效期 30 分钟（可配置）
    """
    # 查询用户
    result = await db.execute(
        select(User).where(User.username == data.username)
    )
    user = result.scalar_one_or_none()

    # 验证用户和密码
    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )

    # 创建 Token
    access_token, expires_in = create_access_token(subject=user.id)

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="获取当前用户信息",
)
async def get_me(current_user: CurrentUserDep) -> User:
    """获取当前登录用户的详细信息."""
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="更新当前用户信息",
)
async def update_me(
    db: DBDep,
    current_user: CurrentUserDep,
    data: UserUpdate,
) -> User:
    """更新当前用户的信息（邮箱或密码）."""
    if data.email is not None:
        # 检查邮箱是否已被其他用户使用
        result = await db.execute(
            select(User).where(
                User.email == str(data.email),
                User.id != current_user.id,
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use",
            )
        current_user.email = str(data.email)

    if data.password is not None:
        current_user.hashed_password = get_password_hash(data.password)

    await db.commit()
    await db.refresh(current_user)

    return current_user
