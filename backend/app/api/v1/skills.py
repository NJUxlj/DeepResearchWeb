"""Skill 配置 API."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import CurrentUserDep, DBDep
from app.models.skill_config import SkillConfig
from app.schemas.skill import (
    SkillConfigCreate,
    SkillConfigResponse,
    SkillConfigUpdate,
)

router = APIRouter(prefix="/skills", tags=["skills"])


class SkillListResponse(BaseModel):
    items: list[SkillConfigResponse]
    total: int


@router.get("", response_model=SkillListResponse)
async def list_skills(
    db: DBDep,
    current_user: CurrentUserDep,
):
    """获取用户 Skill 配置列表."""
    result = await db.execute(
        select(SkillConfig).where(SkillConfig.user_id == current_user.id)
    )
    skills = result.scalars().all()
    return SkillListResponse(
        items=skills,
        total=len(skills)
    )


@router.post("", response_model=SkillConfigResponse, status_code=201)
async def create_skill(
    db: DBDep,
    current_user: CurrentUserDep,
    data: SkillConfigCreate,
):
    """创建 Skill 配置."""
    skill = SkillConfig(
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        trigger_keywords=data.trigger_keywords,
        system_prompt=data.system_prompt,
        required_tools=data.required_tools,
        enabled=data.enabled,
    )
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return skill


@router.put("/{skill_id}", response_model=SkillConfigResponse)
async def update_skill(
    db: DBDep,
    current_user: CurrentUserDep,
    skill_id: int,
    data: SkillConfigUpdate,
):
    """更新 Skill 配置."""
    result = await db.execute(
        select(SkillConfig).where(
            SkillConfig.id == skill_id,
            SkillConfig.user_id == current_user.id,
        )
    )
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(skill, field, value)

    await db.commit()
    await db.refresh(skill)
    return skill


@router.delete("/{skill_id}", status_code=204)
async def delete_skill(
    db: DBDep,
    current_user: CurrentUserDep,
    skill_id: int,
):
    """删除 Skill 配置."""
    result = await db.execute(
        select(SkillConfig).where(
            SkillConfig.id == skill_id,
            SkillConfig.user_id == current_user.id,
        )
    )
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    await db.delete(skill)
    await db.commit()


@router.patch("/{skill_id}/toggle", response_model=SkillConfigResponse)
async def toggle_skill(
    db: DBDep,
    current_user: CurrentUserDep,
    skill_id: int,
    data: dict,
):
    """启用/禁用 Skill."""
    result = await db.execute(
        select(SkillConfig).where(
            SkillConfig.id == skill_id,
            SkillConfig.user_id == current_user.id,
        )
    )
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    skill.enabled = data.get("enabled", not skill.enabled)
    await db.commit()
    await db.refresh(skill)
    return skill
