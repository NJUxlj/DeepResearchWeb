"""用户环境配置数据模型."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class UserEnvConfig(Base):
    """用户环境配置模型 - 存储每个用户的自定义环境变量配置."""

    __tablename__ = "user_env_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # 配置名称（可选，用于区分不同环境如 dev/prod）
    config_name: Mapped[str] = mapped_column(String(100), default="default")
    # 环境变量 JSON 存储
    env_config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="env_configs")

    # 唯一约束：每个用户每个配置名称只能有一条记录
    __table_args__ = (
        UniqueConstraint("user_id", "config_name", name="uq_user_config_name"),
    )

    def __repr__(self) -> str:
        return f"<UserEnvConfig(id={self.id}, user_id={self.user_id}, config_name={self.config_name})>"
