"""消息数据模型."""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.session import Session


class Message(Base):
    """消息模型."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # "user" | "assistant" | "system"
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # 思维链内容（Chain of Thought）
    thinking: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)

    # 引用信息（JSON 格式存储引用列表）
    citations: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True, default=None
    )

    # 消息元数据（如 token 数、模型信息等）
    meta_info: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True, default=None
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )

    # 关系
    session: Mapped["Session"] = relationship("Session", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, session_id={self.session_id}, role={self.role})>"
