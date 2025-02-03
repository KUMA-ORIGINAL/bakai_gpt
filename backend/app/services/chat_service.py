from typing import Annotated
from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
import logging

from models import db_helper, Chat, Message
from schemas.chat import ChatSchema

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(
        self,
        db_session: Annotated[
            AsyncSession,
            Depends(db_helper.session_getter),
        ]
    ):
        self.db_session = db_session

    async def update_chat(self, chat_id: int, **kwargs) -> ChatSchema:
        try:
            stmt = (
                update(Chat)
                .where(Chat.id == chat_id)
                .values(**kwargs)
            )
            await self.db_session.execute(stmt)
            updated_chat = await self.db_session.get(Chat, chat_id)
            return ChatSchema.from_orm(updated_chat)
        except SQLAlchemyError as e:
            logger.error(f"Error updating chat {chat_id}: {str(e)}")
            await self.db_session.rollback()  # Откат транзакции при ошибке
            raise ValueError(f"Failed to update chat: {str(e)}")

    async def get_user_chats(self, user_id: int) -> list[ChatSchema]:
        try:
            stmt = (
                select(Chat)
                .where(Chat.user_id == user_id)
                .options(selectinload(Chat.messages))  # Предзагрузка сообщений
            )
            result = await self.db_session.execute(stmt)
            chats = result.scalars().all()
            return [ChatSchema.from_orm(chat) for chat in chats]
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving chats for user {user_id}: {str(e)}")
            raise ValueError(f"Failed to retrieve user chats: {str(e)}")

    async def get_or_create_chat(self, user_id: int, assistant_id: int) -> ChatSchema:
        try:
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
            return ChatSchema.from_orm(chat)
        except SQLAlchemyError as e:
            logger.error(f"Error getting or creating chat for user {user_id} and assistant {assistant_id}: {str(e)}")
            await self.db_session.rollback()
            raise ValueError(f"Failed to get or create chat: {str(e)}")

    async def create_message(self, chat_id: int, sender: str, content: str) -> Message:
        try:
            message = Message(chat_id=chat_id, sender=sender, content=content)
            self.db_session.add(message)
            await self.db_session.commit()
            await self.db_session.refresh(message)
            return message
        except SQLAlchemyError as e:
            logger.error(f"Error creating message in chat {chat_id} from {sender}: {str(e)}")
            await self.db_session.rollback()
            raise ValueError(f"Failed to create message: {str(e)}")
