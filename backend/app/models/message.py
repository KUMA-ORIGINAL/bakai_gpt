from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String

from .common.base import Base
from .common.mixins import IntIdPkMixin, TimestampMixin


class Message(Base, IntIdPkMixin, TimestampMixin):
    sender: Mapped[str] = mapped_column(String(50))  # 'user' или 'assistant'
    content: Mapped[str] = mapped_column(String(1000))  # Текст сообщения

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id", ondelete=''))
    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")

    files: Mapped[list["File"]] = relationship(
        "File",
        lazy="selectin",
        back_populates="message",
        cascade="all, delete-orphan"
    )
