from fastapi import APIRouter, Depends, Query

from api.dependencies import get_current_user, get_assistant
from schemas.chat import ChatSchema
from services.chat_service import ChatService

router = APIRouter(tags=['chats'])


# @router.get("/", response_model=list[ChatSchema])
# async def get_user_chats(
#     user_id: int = Depends(get_current_user),  # Получаем текущего пользователя
#     chat_service: ChatService = Depends(),
# ):
#     chats = await chat_service.get_user_chats(user_id)
#     return chats


@router.get("/", response_model=ChatSchema)
async def select_assistant(
    user_id: int = Query(..., alias="user_id"),  # Query параметр external_id
    assistant_id: int = Query(..., alias="assistant_id"),
    chat_service: ChatService = Depends(),
):
    chat = await chat_service.get_or_create_chat(user_id, assistant_id)
    return chat
