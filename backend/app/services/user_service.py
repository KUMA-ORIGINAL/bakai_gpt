from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import db_helper, User
from schemas.user import UserCreateSchema


class UserService:
    def __init__(
            self,
            db_session: Annotated[
                AsyncSession,
                Depends(db_helper.session_getter),
            ]
    ):
        self.db_session = db_session

    async def create_user(self, user_data: UserCreateSchema):
        stmt = select(User).where(User.user_external_id == user_data.user_external_id)
        result = await self.db_session.execute(stmt)
        existing_user = result.scalars().first()

        if existing_user:
            raise ValueError(f"Пользователь с external_id={user_data.user_external_id} уже "
                             f"существует")

        user_dict = user_data.model_dump()
        user = User(**user_dict)
        self.db_session.add(user)
        await self.db_session.commit()
        await self.db_session.refresh(user)
        return user

    async def get_user_by_external_id(self, user_external_id: int) -> User:
        stmt = select(User).where(User.user_external_id == user_external_id)
        result = await self.db_session.execute(stmt)
        return result.scalars().first()

    async def get_user_by_id(self, user_id: int) -> User:
        stmt = select(User).where(User.id == user_id)
        result = await self.db_session.execute(stmt)
        return result.scalars().first()
