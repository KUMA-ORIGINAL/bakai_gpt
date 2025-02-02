import traceback

import anyio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, WebSocketException
from starlette.concurrency import run_until_first_complete

from api.dependencies import get_assistant, get_current_user
from schemas.message_to_channel_schema import MessageToChannelSchema
from schemas.request_models import ChatRequest
from services.assistant_service import AssistantService
from services.openai_service import get_assistant_response
from managers.connection import ConnectionManager
from services.chat_service import ChatService
import logging

from services.redis_service import broadcast

router = APIRouter(tags=['ws'])
manager = ConnectionManager()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# @router.websocket("/chats/{user_id}/{assistant_id}")
# async def chat_websocket(
#     websocket: WebSocket,
#     assistant_id: int,
#     user_id: int,
#     chat_service: ChatService = Depends(),
#     assistant_service: AssistantService = Depends(),
# ):
#     logger.info(f"WebSocket connection attempt by user: {user_id} and assistant: {assistant_id}")
#     await websocket.accept()
#     logger.info(f"Пользователь {user_id} подключился к WebSocket")
#
#     assistant = await assistant_service.get_assistant_by_id(assistant_id)
#     chat = await chat_service.get_or_create_chat(user_id, assistant_id)
#     channel = f"chat_{user_id}_{assistant_id}"
#
#     try:
#         async with broadcast.subscribe(channel) as subscriber:
#             logger.info(f"Пользователь {user_id} подписан на канал {channel}")
#
#             try:
#                 async for event in subscriber:
#                     data = await websocket.receive_text()
#                     logger.info(f"Получено сообщение от пользователя {user_id}: {data}")
#
#                     try:
#                         request = ChatRequest(message=data)
#                         user_message = request.message
#
#                         await chat_service.create_message(chat.id, sender="user",
#                                                           content=user_message)
#
#                         full_response = ""
#                         async for response_text in get_assistant_response(user_message, assistant):
#                             # Публикация ответа в канал
#                             await websocket.send_text(e)
#                             logger.info(
#                                 f"Отправлено сообщение пользователю {user_id}: {response_text}")
#
#                             full_response += response_text
#
#                         # Сохранение ответа ассистента
#                         await chat_service.create_message(chat.id, sender="assistant",
#                                                           content=full_response)
#
#                     except Exception as e:
#                         logger.error(f"Ошибка при обработке запроса от пользователя {user_id}: {e}")
#                         await websocket.send_text("Произошла ошибка при обработке вашего запроса.")
#
#             except WebSocketDisconnect:
#                 logger.info(f"Пользователь {user_id} отключился")
#
#                 # Отписка от канала при отключении
#                 await broadcast.unsubscribe(channel)
#
#     except Exception as e:
#         logger.error(f"Ошибка в WebSocket-соединении для пользователя {user_id}: {e}")
#         await websocket.send_text("Произошла ошибка при подключении.")

@router.websocket("/chats/{user_id}/{assistant_id}")
async def chat_websocket(
    websocket: WebSocket,
    assistant_id: int,
    user_id: int,
    chat_service: ChatService = Depends(),
    assistant_service: AssistantService = Depends(),
):
    await websocket.accept()

    try:
        logger.info(f"Client {user_id} connected to assistant {assistant_id}")

        await websocket.send_text(f"Connected to chat {user_id} with assistant {assistant_id}")
        logger.info(f"Sent connection confirmation to user {user_id}")

        assistant = await assistant_service.get_assistant_by_id(assistant_id)
        chat = await chat_service.get_or_create_chat(user_id, assistant_id)
        channel_id = f"chat_{user_id}_{assistant_id}"

        logger.info(f"Chat {chat.id} initialized between user {user_id} and assistant {assistant_id}")

        async with anyio.create_task_group() as task_group:
            async def run_chatroom_ws_receiver() -> None:
                await chatroom_ws_receiver(websocket, channel_id, chat, chat_service)
                task_group.cancel_scope.cancel()
            task_group.start_soon(run_chatroom_ws_receiver)
            await chatroom_ws_sender(websocket, channel_id, chat, chat_service, assistant)

    except WebSocketDisconnect:
        logger.warning(f"User {user_id} disconnected.")
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)


async def chatroom_ws_receiver(websocket: WebSocket, channel: str, chat, chat_service):
    try:
        async for data in websocket.iter_json():
            message_sent = data["message"]
            user_id = data["user_id"]

            # Логируем получение сообщения
            logger.info(f"Received message from user {user_id}: {message_sent}")

            # Создаем и сохраняем сообщение
            message = MessageToChannelSchema(message=message_sent, channel_id=channel, user_id=user_id)
            await chat_service.create_message(chat.id, sender="user", content=message_sent)

            # Публикуем сообщение
            await broadcast.publish(channel=channel, message=message_sent)
            logger.info(f"Published message to channel {channel}: {message_sent}")

    except WebSocketDisconnect:
        logger.warning(f"User disconnected during message reception.")
    except Exception as e:
        logger.error(f"An error occurred in receiver: {e}", exc_info=True)


async def chatroom_ws_sender(websocket: WebSocket, channel: str, chat, chat_service, assistant):
    try:
        async with broadcast.subscribe(channel=channel) as subscriber:
            async for event in subscriber:
                user_message = event.message

                # Логируем получение сообщения из канала
                logger.info(f"Received event for channel {channel}: {user_message}")

                # Генерация ответа ассистента
                full_response = ""
                async for response_text in get_assistant_response(user_message, assistant):
                    await websocket.send_text(response_text)
                    full_response += response_text

                # Сохранение ответа ассистента в базе данных
                await chat_service.create_message(chat.id, sender="assistant", content=full_response)
                logger.info(f"Assistant response sent: {full_response}")

    except WebSocketDisconnect:
        logger.warning(f"User disconnected during message sending.")
    except Exception as e:
        logger.error(f"An error occurred in sender: {e}", exc_info=True)
