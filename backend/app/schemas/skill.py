"""Skill 相关 Schema."""

from datetime import datetime

from pydantic import BaseModel, Field


class SkillConfigBase(BaseModel):
    """Skill 配置基础 Schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str
    trigger_keywords: str = ""
    system_prompt: str
    required_tools: list[str] = Field(default_factory=list)
    enabled: bool = True


class SkillConfigCreate(SkillConfigBase):
    """创建 Skill 配置."""

    pass


class SkillConfigUpdate(BaseModel):
    """更新 Skill 配置."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    trigger_keywords: str | None = None
    system_prompt: str | None = None
    required_tools: list[str] | None = None
    enabled: bool | None = None


class SkillConfigResponse(SkillConfigBase):
    """Skill 配置响应."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
