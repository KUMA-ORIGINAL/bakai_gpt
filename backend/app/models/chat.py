from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .common.base import Base
from .common.mixins import IntIdPkMixin, TimestampMixin


class Chat(Base, IntIdPkMixin, TimestampMixin):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assistant_id: Mapped[int] = mapped_column(ForeignKey("assistants.id"))
    thread_id: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="chats", lazy="joined")
    assistant: Mapped["Assistant"] = relationship("Assistant", lazy="joined")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="chat",
                                                     lazy="selectin", cascade='all, delete-orphan',
                                                     order_by="Message.created_at")
