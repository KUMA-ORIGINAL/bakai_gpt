from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .common.base import Base
from .common.mixins import IntIdPkMixin, TimestampMixin


class File(Base, IntIdPkMixin, TimestampMixin):
    filename: Mapped[str] = mapped_column(String(255))
    file_id: Mapped[str] = mapped_column(String(255))

    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id", ondelete="CASCADE"))
    message: Mapped["Message"] = relationship("Message", back_populates="files")
