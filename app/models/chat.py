from datetime import datetime

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Text, func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.base import Base
from app.models.enums import ChatSenderType

class ChatSession(Base):
    __tablename__ = "chat_session"

    session_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey(
            "patient.user_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    patient = relationship(
        "Patient",
        back_populates="chat_session",
    )

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    appointment = relationship(
        "Appointment",
        back_populates="chat_session",
        uselist=False,
    )

class ChatMessage(Base):
    __tablename__ = "chat_message"

    message_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    session_id: Mapped[int] = mapped_column(
        ForeignKey(
            "chat_session.session_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    sender_type: Mapped[ChatSenderType] = mapped_column(
        SQLEnum(
            ChatSenderType,
            name="chat_sender_type",
        ),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    intent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    session = relationship(
        "ChatSession",
        back_populates="messages",
    )