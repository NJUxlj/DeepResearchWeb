"""User 模型测试."""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.security import verify_password
from app.models.user import User


@pytest.mark.unit
class TestUserModel:
    """User 模型测试类."""

    async def test_create_user(self, db_session) -> None:
        """测试创建用户."""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.is_superuser is False

    async def test_user_unique_username(self, db_session) -> None:
        """测试用户名唯一性."""
        user1 = User(
            username="uniqueuser",
            email="user1@example.com",
            hashed_password="pass1",
        )
        user2 = User(
            username="uniqueuser",  # 相同用户名
            email="user2@example.com",
            hashed_password="pass2",
        )

        db_session.add(user1)
        await db_session.commit()

        db_session.add(user2)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_user_unique_email(self, db_session) -> None:
        """测试邮箱唯一性."""
        user1 = User(
            username="user1",
            email="unique@example.com",
            hashed_password="pass1",
        )
        user2 = User(
            username="user2",
            email="unique@example.com",  # 相同邮箱
            hashed_password="pass2",
        )

        db_session.add(user1)
        await db_session.commit()

        db_session.add(user2)
        with pytest.raises(IntegrityError):
            await db_session.commit()

    async def test_user_relationships(self, db_session) -> None:
        """测试用户关系."""
        from app.models.session import Session

        user = User(
            username="relationuser",
            email="relation@example.com",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()

        # 创建会话
        session = Session(
            user_id=user.id,
            title="Test Session",
            mode="chat",
        )
        db_session.add(session)
        await db_session.commit()

        # 查询并验证关系
        result = await db_session.execute(
            select(User).where(User.id == user.id)
        )
        fetched_user = result.scalar_one()
        assert len(fetched_user.sessions) == 1

    async def test_user_default_values(self, db_session) -> None:
        """测试用户默认字段值."""
        user = User(
            username="defaultuser",
            email="default@example.com",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.is_active is True
        assert user.is_superuser is False
        assert user.created_at is not None

    async def test_user_repr(self, db_session) -> None:
        """测试用户字符串表示."""
        user = User(
            username="repruser",
            email="repr@example.com",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()

        repr_str = repr(user)
        assert "repruser" in repr_str
        assert "repr@example.com" in repr_str
