import base64
import json
from pathlib import Path
from typing import Annotated

import anyio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, WebSocketException
from starlette import status

from api.dependencies import get_chat_service, verify_user_ws
from services.openai_service import get_assistant_response, upload_file_to_openai
from managers.connection import ConnectionManager
from services.chat_service import ChatService
import logging

from services.redis_service import broadcast

router = APIRouter(tags=['ws'])
manager = ConnectionManager()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.websocket("/chats/{chat_id}/")
async def chat_websocket(
    websocket: WebSocket,
    chat_id: int,
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    user_id: int = Depends(verify_user_ws)
):
    await websocket.accept()

    try:
        chat = await chat_service.get_chat(chat_id)
        if not chat:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason=f"Chat with ID {chat_id} does not exist."
            )
        logger.info(f"Client {chat.user_id} connected to chat {chat_id}")

        await websocket.send_json({'message': 'Connected',
                                   'user_id': chat.user_id,
                                   'assistant_id': chat.assistant_id})
        channel_id = f"chat_{chat_id}"

        async with anyio.create_task_group() as task_group:
            async def run_chatroom_ws_receiver() -> None:
                await chatroom_ws_receiver(websocket, channel_id, chat, chat_service)
                task_group.cancel_scope.cancel()
            task_group.start_soon(run_chatroom_ws_receiver)
            await chatroom_ws_sender(websocket, channel_id, chat, chat_service, chat.assistant)

    except WebSocketException as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except WebSocketDisconnect:
        logger.warning(f"Chat {chat_id} disconnected.")
        await websocket.close(code=status.WS_1001_GOING_AWAY)
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


async def chatroom_ws_receiver(websocket: WebSocket, channel: str, chat, chat_service):
    try:
        async for data in websocket.iter_json():
            text = data.get("text")
            files = data.get("files", [])

            await chat_service.update_chat(chat.id, name=text[:30])
            await chat_service.create_message_with_files(chat.id, sender="user", content=text, files=files)

            await broadcast.publish(channel=channel, message=json.dumps({
                "text": text,
                "files": files
            }))
            logger.info(f"Published message to channel {channel}: text + {len(files)} files.")

    except WebSocketDisconnect:
        logger.warning(f"User disconnected during message reception.")
    except Exception as e:
        logger.error(f"An error occurred in receiver: {e}", exc_info=True)


async def chatroom_ws_sender(websocket: WebSocket, channel: str, chat, chat_service, assistant):
    try:
        async with broadcast.subscribe(channel=channel) as subscriber:
            async for event in subscriber:
                event_data = json.loads(event.message)

                user_text = event_data.get("text")
                uploaded_files = event_data.get("files", [])

                logger.info(f"Received event for channel {channel}: {user_text} + files: {uploaded_files}")

                file_ids = []
                b64_images = []

                for f in uploaded_files:
                    if f['type'] == 'image':
                        b64_images.append(f['base64_image'])
                    elif f['type'] == "file":
                        file_ids.append(f['file_id'])
                    else:
                        logger.info(f"Skipping unsupported file: {f}")

                full_response = ""
                async for response_text in get_assistant_response(
                    user_text,
                    chat,
                    assistant,
                    chat_service,
                    file_ids=file_ids,  # только допустимые
                    b64_images=b64_images   # нововведение
                ):
                    await websocket.send_text(response_text)
                    full_response += response_text

                await websocket.send_text("[COMPLETE]")
                await chat_service.create_message(chat.id, sender="assistant", content=full_response)

                logger.info(f"Assistant response sent: {full_response}")

    except WebSocketDisconnect:
        logger.warning(f"User disconnected during message sending.")
    except Exception as e:
        logger.error(f"An error occurred in sender: {e}", exc_info=True)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)