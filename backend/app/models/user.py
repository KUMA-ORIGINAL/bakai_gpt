from sqlalchemy import String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .common.base import Base
from .common.mixins import IntIdPkMixin, TimestampMixin


class User(Base, IntIdPkMixin, TimestampMixin):
    external_id: Mapped[int] = mapped_column(unique=True)
    full_name: Mapped[str] = mapped_column(String(50), nullable=False)

    chats: Mapped[list["Chat"]] = relationship("Chat", back_populates="user")
