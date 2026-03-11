"""用户通知设置数据模型."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class UserNotificationSettings(Base):
    """用户通知设置模型."""

    __tablename__ = "user_notification_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    # 通知设置 JSON
    settings: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="notification_settings")

    def __repr__(self) -> str:
        return f"<UserNotificationSettings(id={self.id}, user_id={self.user_id})>"
