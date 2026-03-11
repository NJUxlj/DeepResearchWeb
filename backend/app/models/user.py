"""用户数据模型."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.session import Session
    from app.models.research_task import ResearchTask
    from app.models.tool_config import ToolConfig
    from app.models.skill_config import SkillConfig
    from app.models.mcp_config import MCPServerConfig
    from app.models.user_env_config import UserEnvConfig
    from app.models.user_notification_settings import UserNotificationSettings


class User(Base):
    """用户模型."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # 关系
    sessions: Mapped[list["Session"]] = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
    research_tasks: Mapped[list["ResearchTask"]] = relationship(
        "ResearchTask", back_populates="user", cascade="all, delete-orphan"
    )
    tool_configs: Mapped[list["ToolConfig"]] = relationship(
        "ToolConfig", back_populates="user", cascade="all, delete-orphan"
    )
    skill_configs: Mapped[list["SkillConfig"]] = relationship(
        "SkillConfig", back_populates="user", cascade="all, delete-orphan"
    )
    mcp_configs: Mapped[list["MCPServerConfig"]] = relationship(
        "MCPServerConfig", back_populates="user", cascade="all, delete-orphan"
    )
    env_configs: Mapped[list["UserEnvConfig"]] = relationship(
        "UserEnvConfig", back_populates="user", cascade="all, delete-orphan"
    )
    notification_settings: Mapped["UserNotificationSettings"] = relationship(
        "UserNotificationSettings", back_populates="user", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
