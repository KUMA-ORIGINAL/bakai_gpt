from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError
import logging

from models import Chat, Message, File
from schemas.chat import ChatSchema

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_all_chats(self, user_id: int) -> List[Chat]:
        try:
            stmt = (
                select(Chat)
                .where(Chat.user_id == user_id)
                .options(
                    joinedload(Chat.user),
                    joinedload(Chat.assistant),
                )
                .order_by(Chat.created_at.desc())
            )
            result = await self.db_session.execute(stmt)
            chats = result.scalars().all()
            return chats
        except SQLAlchemyError as e:
            logger.error(
                f"Error getting chats for user {user_id}: {str(e)}", exc_info=True)
            raise e

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
            logger.error(f"Error updating chat {chat_id}: {str(e)}", exc_info=True)
            await self.db_session.rollback()
            raise e

    async def get_chat(self, chat_id: int) -> Optional[Chat]:
        try:
            stmt = (
                select(Chat)
                .where(Chat.id == chat_id)
                .options(
                    joinedload(Chat.user),
                    joinedload(Chat.assistant),
                    selectinload(Chat.messages).selectinload(Message.files)
                )
            )
            result = await self.db_session.execute(stmt)
            chat: Optional[Chat] = result.scalars().first()
            return chat
        except SQLAlchemyError as e:
            logger.error(f"Error getting chat for id {chat_id}: {str(e)}", exc_info=True)
            raise

    async def create_chat(self, user_id: int, assistant_id: int) -> Chat:
        try:
            chat = Chat(user_id=user_id, assistant_id=assistant_id)
            self.db_session.add(chat)
            await self.db_session.commit()
            await self.db_session.refresh(chat)
            logger.info(f"Creating new chat for user {user_id} and assistant {assistant_id}")
            return chat
        except SQLAlchemyError as e:
            logger.error(
                f"Error creating chat for user {user_id} and assistant {assistant_id}: {str(e)}",
                exc_info=True)
            await self.db_session.rollback()
            raise e

    async def create_message(self, chat_id: int, sender: str, content: str) -> Message:
        try:
            message = Message(chat_id=chat_id, sender=sender, content=content)
            self.db_session.add(message)
            await self.db_session.commit()
            logger.info(f"Message created in chat {chat_id} by {sender}: {content}")
            return message
        except SQLAlchemyError as e:
            logger.error(f"Error creating message in chat {chat_id} from {sender}: {str(e)}", exc_info=True)
            await self.db_session.rollback()
            raise e

    async def create_file(self, message_id: int, file_id: str, filename: str) -> File:
        try:
            file = File(message_id=message_id, file_id=file_id, filename=filename)
            self.db_session.add(file)
            await self.db_session.commit()
            logger.info(f"File created for message {message_id}: {filename}")
            return file
        except SQLAlchemyError as e:
            logger.error(f"Error creating file for message {message_id}: {str(e)}", exc_info=True)
            await self.db_session.rollback()
            raise

    async def create_message_with_files(self, chat_id: int, sender: str, content: str, files: list[dict]) -> Message:
        try:
            message = Message(
                chat_id=chat_id,
                sender=sender,
                content=content,
                files=[
                    File(file_id=f["file_id"], filename=f["filename"]) for f in files
                ]
            )
            self.db_session.add(message)
            await self.db_session.commit()
            logger.info(f"Message with files created in chat {chat_id} by {sender}")
            return message
        except SQLAlchemyError as e:
            logger.error(f"Error creating message with files: {e}", exc_info=True)
            await self.db_session.rollback()
            raise

    async def delete_chat(self, chat: Chat):
        try:
            await self.db_session.delete(chat)
            await self.db_session.commit()
        except SQLAlchemyError as e:
            logger.exception(f"Error deleting chat {chat.id}")
            await self.db_session.rollback()
            raise e
