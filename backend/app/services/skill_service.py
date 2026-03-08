"""Skill 执行服务."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill_config import SkillConfig


class SkillService:
    """Skill 执行服务."""

    def __init__(self):
        self._skill_cache: dict[str, SkillConfig] = {}

    async def find_skill_by_keyword(
        self,
        db: AsyncSession,
        user_id: int,
        keyword: str,
    ) -> SkillConfig | None:
        """根据关键词查找匹配的 Skill.

        Args:
            db: 数据库会话
            user_id: 用户 ID
            keyword: 关键词

        Returns:
            匹配的 Skill 或 None
        """
        result = await db.execute(
            select(SkillConfig).where(
                SkillConfig.user_id == user_id,
                SkillConfig.enabled == True,  # noqa: E712
            )
        )
        skills = result.scalars().all()

        for skill in skills:
            if skill.trigger_keywords:
                keywords = [
                    k.strip().lower()
                    for k in skill.trigger_keywords.split(",")
                ]
                if keyword.lower() in keywords:
                    return skill

        return None

    async def get_skill_prompt(
        self,
        db: AsyncSession,
        user_id: int,
        skill_id: int,
    ) -> str | None:
        """获取 Skill 的系统 Prompt.

        Args:
            db: 数据库会话
            user_id: 用户 ID
            skill_id: Skill ID

        Returns:
            系统 Prompt 或 None
        """
        result = await db.execute(
            select(SkillConfig).where(
                SkillConfig.id == skill_id,
                SkillConfig.user_id == user_id,
            )
        )
        skill = result.scalar_one_or_none()

        if skill:
            return skill.system_prompt
        return None

    def apply_skill_template(
        self,
        system_prompt: str,
        context: dict[str, Any],
    ) -> str:
        """应用 Skill 模板，填充上下文变量.

        Args:
            system_prompt: 系统 Prompt 模板
            context: 上下文变量

        Returns:
            填充后的 Prompt
        """
        result = system_prompt
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, str(value))
        return result


# 全局 Skill 服务实例
skill_service = SkillService()
