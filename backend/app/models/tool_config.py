"""工具配置数据模型."""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class ToolConfig(Base):
    """工具配置模型."""

    __tablename__ = "tool_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # 工具类型: builtin | custom
    tool_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # 工具配置（JSON Schema 参数定义）
    config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # 是否启用
    enabled: Mapped[bool] = mapped_column(default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="tool_configs")

    def __repr__(self) -> str:
        return f"<ToolConfig(id={self.id}, name={self.name}, type={self.tool_type})>"
