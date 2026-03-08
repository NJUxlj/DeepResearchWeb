"""MCP 服务器配置数据模型."""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class MCPServerConfig(Base):
    """MCP 服务器配置模型."""

    __tablename__ = "mcp_server_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")

    # 传输类型: stdio | sse
    transport: Mapped[str] = mapped_column(String(10), nullable=False)

    # stdio 传输配置
    command: Mapped[str | None] = mapped_column(String(255), nullable=True)
    args: Mapped[list[str]] = mapped_column(JSON, default=list)
    env: Mapped[dict[str, str]] = mapped_column(JSON, default=dict)

    # sse 传输配置
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # 是否启用
    enabled: Mapped[bool] = mapped_column(default=True, nullable=False)

    # 缓存的工具列表（避免每次都连接获取）
    cached_tools: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSON, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="mcp_configs")

    def __repr__(self) -> str:
        return f"<MCPServerConfig(id={self.id}, name={self.name}, transport={self.transport})>"
