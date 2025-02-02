from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from api.dependencies import get_assistant, get_current_user
from schemas.request_models import ChatRequest
from services.assistant_service import AssistantService
from services.openai_service import get_assistant_response
from managers.connection import ConnectionManager
from services.chat_service import ChatService
import logging

router = APIRouter(tags=['ws'])
manager = ConnectionManager()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.websocket("/chats/{user_id}/{assistant_id}")
async def chat_websocket(
    websocket: WebSocket,
    assistant_id: int,
    user_id: int,
    chat_service: ChatService = Depends(),
    assistant_service: AssistantService = Depends(),
):
    logger.info(f"WebSocket connection attempt by user: {user_id} and assistant: {assistant_id}")
    await manager.connect(websocket, user_id)
    logger.info(f"Пользователь {user_id} подключился к WebSocket")

    assistant = await assistant_service.get_assistant_by_id(assistant_id)
    chat = await chat_service.get_or_create_chat(user_id, assistant_id)

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Получено сообщение от пользователя {user_id}: {data}")

            try:
                request = ChatRequest(message=data)
                user_message = request.message

                await chat_service.create_message(chat.id, sender="user", content=user_message)

                full_response = ""

                async for response_text in get_assistant_response(user_message, assistant):
                    await manager.send_message_to_user(response_text, user_id)
                    logger.info(f"Отправлено сообщение пользователю {user_id}: {response_text}")

                    full_response += response_text

                await chat_service.create_message(chat.id, sender="assistant",
                                                  content=full_response)

            except Exception as e:
                logger.error(f"Ошибка при обработке запроса от пользователя {user_id}: {e}")
                await manager.send_message(
                    "Произошла ошибка при обработке вашего запроса.",
                    websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"Пользователь {user_id} отключился")
