"""用户环境配置 Pydantic Schema."""

from datetime import datetime
from typing import Dict

from pydantic import BaseModel, Field


class UserEnvConfigBase(BaseModel):
    """用户环境配置基础 Schema."""

    config_name: str = Field(default="default", description="配置名称，如 default, dev, prod")


class UserEnvConfigCreate(UserEnvConfigBase):
    """用户环境配置创建 Schema."""

    env_config: Dict[str, str] = Field(default_factory=dict, description="环境变量字典")


class UserEnvConfigUpdate(BaseModel):
    """用户环境配置更新 Schema."""

    env_config: Dict[str, str] = Field(..., description="环境变量字典")


class UserEnvConfigResponse(UserEnvConfigBase):
    """用户环境配置响应 Schema."""

    id: int
    user_id: int
    env_config: Dict[str, str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserEnvConfigInitResponse(BaseModel):
    """用户环境配置初始化响应 - 包含从 .env 文件读取的默认值"""

    env_config: Dict[str, str]
    is_new: bool = Field(description="是否是新建的配置（之前没有保存过）")
