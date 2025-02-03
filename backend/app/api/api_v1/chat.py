from typing import Annotated

from fastapi import APIRouter, Depends, Query, HTTPException

from api.dependencies import get_chat_service, get_assistant_service, get_user_service
from schemas.chat import ChatSchema
from services.assistant_service import AssistantService
from services.chat_service import ChatService
from services.user_service import UserService

router = APIRouter(tags=['chats'])


@router.get("/", response_model=ChatSchema)
async def get_chat(
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    assistant_service: Annotated[AssistantService, Depends(get_assistant_service)],
    user_id: int = Query(..., alias="user_id"),
    assistant_id: int = Query(..., alias="assistant_id"),
):
    user_exists = await user_service.get_user_by_id(user_id=user_id)
    if not user_exists:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} does not exist.")

    assistant_exists = await assistant_service.get_assistant_by_id(assistant_id=assistant_id)
    if not assistant_exists:
        raise HTTPException(status_code=404,
                            detail=f"Assistant with id {assistant_id} does not exist.")

    chat = await chat_service.get_chat(user_id, assistant_id)
    if not chat:
        chat = await chat_service.create_chat(user_id, assistant_id)

    return ChatSchema.from_orm(chat)


@router.delete("/", response_model=ChatSchema)
async def delete_chat(
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    user_service: Annotated[UserService, Depends(get_user_service)],
    assistant_service: Annotated[AssistantService, Depends(get_assistant_service)],
    user_id: int = Query(..., alias="user_id"),
    assistant_id: int = Query(..., alias="assistant_id"),
):
    user_exists = await user_service.get_user_by_id(user_id=user_id)
    if not user_exists:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} does not exist.")

    assistant_exists = await assistant_service.get_assistant_by_id(assistant_id=assistant_id)
    if not assistant_exists:
        raise HTTPException(status_code=404,
                            detail=f"Assistant with id {assistant_id} does not exist.")

    chat = await chat_service.get_chat(user_id, assistant_id)

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found.")

    await chat_service.delete_chat(chat)

    return ChatSchema.from_orm(chat)
