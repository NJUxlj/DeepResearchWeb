"""Session 和 Message 模型测试."""

import pytest
from sqlalchemy import select

from app.models.message import Message
from app.models.session import Session
from app.models.user import User


@pytest.mark.unit
class TestSessionModel:
    """Session 模型测试."""

    async def test_create_session(self, db_session) -> None:
        """测试创建会话."""
        user = User(
            username="sessionuser",
            email="session@example.com",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()

        session = Session(
            user_id=user.id,
            title="Test Session",
            mode="chat",
        )
        db_session.add(session)
        await db_session.commit()

        assert session.id is not None
        assert session.mode == "chat"

    async def test_create_research_session(self, db_session) -> None:
        """测试创建研究模式会话."""
        user = User(
            username="researchuser",
            email="research@example.com",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()

        session = Session(
            user_id=user.id,
            title="Research Session",
            mode="research",
        )
        db_session.add(session)
        await db_session.commit()

        assert session.mode == "research"

    async def test_session_messages(self, db_session) -> None:
        """测试会话消息关系."""
        user = User(
            username="msguser",
            email="msg@example.com",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()

        session = Session(
            user_id=user.id,
            title="Message Test",
            mode="chat",
        )
        db_session.add(session)
        await db_session.commit()

        # 添加消息
        msg1 = Message(
            session_id=session.id,
            role="user",
            content="Hello",
        )
        msg2 = Message(
            session_id=session.id,
            role="assistant",
            content="Hi there!",
        )
        db_session.add_all([msg1, msg2])
        await db_session.commit()

        # 验证
        result = await db_session.execute(
            select(Session).where(Session.id == session.id)
        )
        fetched_session = result.scalar_one()
        assert len(fetched_session.messages) == 2

    async def test_session_default_values(self, db_session) -> None:
        """测试会话默认字段值."""
        user = User(
            username="defaultsessuser",
            email="defaultsess@example.com",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()

        session = Session(
            user_id=user.id,
            title="Default Test",
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        assert session.mode == "chat"  # 默认模式
        assert session.created_at is not None
        assert session.updated_at is not None

    async def test_session_repr(self, db_session) -> None:
        """测试会话字符串表示."""
        user = User(
            username="reprsessuser",
            email="reprsess@example.com",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()

        session = Session(
            user_id=user.id,
            title="Repr Test",
            mode="chat",
        )
        db_session.add(session)
        await db_session.commit()

        repr_str = repr(session)
        assert "Repr Test" in repr_str


@pytest.mark.unit
class TestMessageModel:
    """Message 模型测试."""

    async def test_create_message(self, db_session) -> None:
        """测试创建消息."""
        user = User(
            username="msgcreateuser",
            email="msgcreate@example.com",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()

        session = Session(
            user_id=user.id,
            title="Message Create Test",
            mode="chat",
        )
        db_session.add(session)
        await db_session.commit()

        message = Message(
            session_id=session.id,
            role="user",
            content="Test message content",
        )
        db_session.add(message)
        await db_session.commit()

        assert message.id is not None
        assert message.role == "user"
        assert message.content == "Test message content"

    async def test_message_with_citations(self, db_session) -> None:
        """测试带引用标记的消息."""
        user = User(
            username="citeuser",
            email="cite@example.com",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()

        session = Session(
            user_id=user.id,
            title="Citation Test",
            mode="chat",
        )
        db_session.add(session)
        await db_session.commit()

        message = Message(
            session_id=session.id,
            role="assistant",
            content="Based on the research...",
            citations={"sources": [{"id": "1", "url": "https://example.com"}]},
        )
        db_session.add(message)
        await db_session.commit()

        assert message.citations is not None
        assert "sources" in message.citations

    async def test_message_with_meta_info(self, db_session) -> None:
        """测试带元数据的消息."""
        user = User(
            username="metamsguser",
            email="metamsg@example.com",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()

        session = Session(
            user_id=user.id,
            title="Meta Test",
            mode="chat",
        )
        db_session.add(session)
        await db_session.commit()

        message = Message(
            session_id=session.id,
            role="assistant",
            content="Response content",
            meta_info={"tokens": 100, "model": "gpt-4"},
        )
        db_session.add(message)
        await db_session.commit()

        assert message.meta_info is not None
        assert message.meta_info["tokens"] == 100

    async def test_message_default_citations(self, db_session) -> None:
        """测试消息引用字段默认值."""
        user = User(
            username="defciteuser",
            email="defcite@example.com",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()

        session = Session(
            user_id=user.id,
            title="Default Citation Test",
            mode="chat",
        )
        db_session.add(session)
        await db_session.commit()

        message = Message(
            session_id=session.id,
            role="user",
            content="Simple message",
        )
        db_session.add(message)
        await db_session.commit()

        assert message.citations is None

    async def test_message_repr(self, db_session) -> None:
        """测试消息字符串表示."""
        user = User(
            username="reprusermsg",
            email="reprusermsg@example.com",
            hashed_password="pass",
        )
        db_session.add(user)
        await db_session.commit()

        session = Session(
            user_id=user.id,
            title="Repr Test",
            mode="chat",
        )
        db_session.add(session)
        await db_session.commit()

        message = Message(
            session_id=session.id,
            role="user",
            content="Test",
        )
        db_session.add(message)
        await db_session.commit()

        repr_str = repr(message)
        assert "user" in repr_str
