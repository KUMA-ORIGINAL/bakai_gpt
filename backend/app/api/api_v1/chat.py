from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File

from api.dependencies import get_chat_service, get_assistant_service, verify_user
from config import settings
from schemas.chat import ChatSchema, ChatListSchema, ChatCreateSchema
from services import upload_file_to_openai
from services.assistant_service import AssistantService
from services.chat_service import ChatService

router = APIRouter(tags=['chats'])


@router.get("/", response_model=list[ChatListSchema])
async def get_chats(
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    user_id: int = Depends(verify_user)
):
    chats = await chat_service.get_all_chats(user_id)
    for chat in chats:
        chat.assistant.photo = f"{settings.BASE_URL}{chat.assistant.photo}"

    return chats


@router.post("/", response_model=ChatSchema)
async def create_chat(
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    assistant_service: Annotated[AssistantService, Depends(get_assistant_service)],
    assistant_id: int = Query(..., alias="assistant_id"),
    user_id: int = Depends(verify_user),
):
    assistant_exists = await assistant_service.get_assistant_by_id(assistant_id=assistant_id)
    if not assistant_exists:
        raise HTTPException(status_code=404,
                            detail=f"Assistant with id {assistant_id} does not exist.")
    new_chat = await chat_service.create_chat(user_id, assistant_id)
    return new_chat


@router.get("/{chat_id}/", response_model=ChatSchema)
async def get_chat(
    chat_id: int,
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    user_id: int = Depends(verify_user),
):
    chat = await chat_service.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail=f"Chat with id {chat_id} does not exist.")

    chat.assistant.photo = f"{settings.BASE_URL}{chat.assistant.photo}"
    return chat


@router.delete("/{chat_id}/", response_model=ChatSchema)
async def delete_chat(
    chat_id: int,
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    user_id: int = Depends(verify_user),
):
    chat = await chat_service.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail=f"Chat with id {chat_id} does not exist.")

    await chat_service.delete_chat(chat)
    return chat


@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_data = await file.read()
        openai_file = await upload_file_to_openai(file_data)
        file_id = openai_file.id
        return {"file_id": file_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке файла в OpenAI: {str(e)}")