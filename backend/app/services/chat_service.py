from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import db_helper, Chat, Message
from schemas.chat import ChatSchema


class ChatService:
    def __init__(
            self,
            db_session: Annotated[
                AsyncSession,
                Depends(db_helper.session_getter),
            ]
    ):
        self.db_session = db_session

    async def get_user_chats(self, user_id: int) -> list[ChatSchema]:
        stmt = select(Chat).where(Chat.user_id == user_id)
        result = await self.db_session.execute(stmt)
        chats = result.scalars().all()
        return [ChatSchema.from_orm(chat) for chat in chats]

    async def get_or_create_chat(self, user_id: int, assistant_id: int) -> ChatSchema:
        stmt = (
            select(Chat)
            .where(
                Chat.user_id == user_id,
                Chat.assistant_id == assistant_id
            )
            .options(
                selectinload(Chat.user),
                selectinload(Chat.assistant),
                selectinload(Chat.messages),
            )
        )
        result = await self.db_session.execute(stmt)
        chat = result.scalars().first()

        if not chat:
            chat = Chat(user_id=user_id, assistant_id=assistant_id)
            self.db_session.add(chat)
            await self.db_session.commit()
            await self.db_session.refresh(chat)

        return ChatSchema.from_orm(chat)

    async def create_message(self, chat_id: int, sender: str, content: str):
        message = Message(chat_id=chat_id, sender=sender, content=content)
        self.db_session.add(message)
        await self.db_session.commit()
        await self.db_session.refresh(message)
        return message
