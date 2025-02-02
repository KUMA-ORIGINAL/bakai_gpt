from sqlalchemy.orm import Mapped, mapped_column

from .common.base import Base
from .common.mixins import IntIdPkMixin


class Assistant(IntIdPkMixin, Base):
    name: Mapped[str] = mapped_column()  # "Юрист", "Психолог"
    description: Mapped[str] = mapped_column()  # Краткое описание ассистента
