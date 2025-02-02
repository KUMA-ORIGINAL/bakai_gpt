import anyio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, WebSocketException
from starlette import status

from schemas.message_to_channel_schema import MessageToChannelSchema
from services.assistant_service import AssistantService
from services.openai_service import get_assistant_response
from managers.connection import ConnectionManager
from services.chat_service import ChatService
import logging

from services.redis_service import broadcast
from services.user_service import UserService

router = APIRouter(tags=['ws'])
manager = ConnectionManager()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.websocket("/chats/{user_id}/{assistant_id}")
async def chat_websocket(
    websocket: WebSocket,
    assistant_id: int,
    user_id: int,
    user_service: UserService = Depends(),
    chat_service: ChatService = Depends(),
    assistant_service: AssistantService = Depends(),
):

    await websocket.accept()

    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason=f"User with ID {user_id} does not exist."
            )
        assistant = await assistant_service.get_assistant_by_id(assistant_id)
        if not assistant:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason=f"Assistant with ID {assistant_id} does not exist."
            )

        logger.info(f"Client {user_id} connected to assistant {assistant_id}")

        await websocket.send_json({'message': 'Connected',
                                   'user_id': user_id,
                                   'assistant_id': assistant_id})
        logger.info(f"Sent connection confirmation to user {user_id}")

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
    except WebSocketException as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)


async def chatroom_ws_receiver(websocket: WebSocket, channel: str, chat, chat_service):
    try:
        async for data in websocket.iter_json():
            message_sent = data["message"]
            user_id = data["user_id"]

            logger.info(f"Received message from user {user_id}: {message_sent}")

            message = MessageToChannelSchema(message=message_sent, channel_id=channel, user_id=user_id)
            await chat_service.create_message(chat.id, sender="user", content=message_sent)

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
                logger.info(f"Received event for channel {channel}: {user_message}")

                full_response = ""
                async for response_text in get_assistant_response(
                        user_message, chat, assistant, chat_service
                ):
                    await websocket.send_text(response_text)
                    full_response += response_text

                await chat_service.create_message(chat.id, sender="assistant", content=full_response)
                logger.info(f"Assistant response sent: {full_response}")

    except WebSocketDisconnect:
        logger.warning(f"User disconnected during message sending.")
    except Exception as e:
        logger.error(f"An error occurred in sender: {e}", exc_info=True)
