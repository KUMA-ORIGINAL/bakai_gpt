from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import text

from models import db_helper
from models import Assistant


class AssistantService:
    def __init__(
        self,
        db_session: Annotated[
            AsyncSession,
            Depends(db_helper.session_getter),
        ]
    ):
        self.db_session = db_session

    async def get_all_assistants(
        self,
        order: str = "id",  # Поле для сортировки
        limit: int = 100,    # Лимит записей
        offset: int = 0      # Смещение
    ):
        stmt = (
            select(Assistant)
            .order_by(text(f"{order} ASC"))  # Сортировка по указанному полю
            .limit(limit)
            .offset(offset)
        )
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_assistant_by_id(self, assistant_id: int):
        stmt = select(Assistant).where(Assistant.id == assistant_id)
        result = await self.db_session.execute(stmt)
        assistant = result.scalars().first()
        return assistant
