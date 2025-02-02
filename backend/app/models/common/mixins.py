from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class IntIdPkMixin:
    id: Mapped[int] = mapped_column(primary_key=True)


class UpdatedAtMixin:
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),  # Автоматически заполняется текущим временем
        onupdate=func.now(),  # Автоматически обновляется при изменении записи
        nullable=False,
    )


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),  # Автоматически заполняется текущим временем
        nullable=False,
    )


class TimestampMixin(UpdatedAtMixin, CreatedAtMixin):
    pass
