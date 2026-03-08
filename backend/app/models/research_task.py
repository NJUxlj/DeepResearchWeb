"""研究任务数据模型."""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.session import Session
    from app.models.user import User


class ResearchTask(Base):
    """研究任务模型，用于追踪 DeepResearch 任务状态."""

    __tablename__ = "research_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 任务状态
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False
    )  # "pending" | "running" | "completed" | "failed"

    # 原始查询
    query: Mapped[str] = mapped_column(Text, nullable=False)

    # 研究配置
    config: Mapped[dict[str, Any] | None] = mapped_column(JSON, default=dict)

    # 执行结果
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 执行统计
    iterations: Mapped[int] = mapped_column(default=0, nullable=False)
    sources_count: Mapped[int] = mapped_column(default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # 关系
    session: Mapped["Session"] = relationship("Session", back_populates="research_tasks")
    user: Mapped["User"] = relationship("User", back_populates="research_tasks")

    def __repr__(self) -> str:
        return f"<ResearchTask(id={self.id}, status={self.status})>"
