from sqlalchemy.orm import relationship, Mapped, mapped_column

from .common.base import Base
from .common.mixins import IntIdPkMixin, TimestampMixin


class User(Base, IntIdPkMixin, TimestampMixin):
    user_external_id: Mapped[int] = mapped_column(unique=True)

    chats: Mapped[list["Chat"]] = relationship("Chat", back_populates="user")
