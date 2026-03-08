"""Skill 配置数据模型."""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class SkillConfig(Base):
    """Skill 配置模型."""

    __tablename__ = "skill_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # 触发关键词（逗号分隔）
    trigger_keywords: Mapped[str] = mapped_column(Text, default="")

    # 系统 Prompt 模板
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)

    # 需要的工具列表
    required_tools: Mapped[list[str]] = mapped_column(JSON, default=list)

    # 是否启用
    enabled: Mapped[bool] = mapped_column(default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="skill_configs")

    def __repr__(self) -> str:
        return f"<SkillConfig(id={self.id}, name={self.name})>"
