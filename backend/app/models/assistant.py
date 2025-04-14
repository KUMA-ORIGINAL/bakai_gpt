from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .common.base import Base
from .common.mixins import IntIdPkMixin


class Assistant(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    photo: Mapped[str] = mapped_column(String(200), nullable=False)
    openai_id: Mapped[str] = mapped_column(String(200), nullable=True)
