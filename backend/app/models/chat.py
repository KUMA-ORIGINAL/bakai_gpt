from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .common.base import Base
from .common.mixins import IntIdPkMixin, TimestampMixin


class Chat(Base, IntIdPkMixin, TimestampMixin):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assistant_id: Mapped[int] = mapped_column(ForeignKey("assistants.id"))

    user: Mapped["User"] = relationship("User", back_populates="chats", lazy="selectin")
    assistant: Mapped["Assistant"] = relationship("Assistant", lazy="selectin")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="chat",
                                                     lazy="selectin")

