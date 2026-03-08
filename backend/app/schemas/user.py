"""用户相关 Pydantic Schema."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """用户基础 Schema."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """用户注册请求 Schema."""

    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码复杂度."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """用户登录请求 Schema."""

    username: str
    password: str


class UserUpdate(BaseModel):
    """用户信息更新 Schema."""

    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8, max_length=100)


class UserResponse(UserBase):
    """用户信息响应 Schema."""

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT Token 响应 Schema."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # 秒


class TokenPayload(BaseModel):
    """JWT Token Payload Schema."""

    sub: int | None = None  # user_id
    exp: datetime | None = None
    type: str = "access"
