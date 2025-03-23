from typing import Annotated

from fastapi import APIRouter, Depends, Request

from api.dependencies import get_assistant_service
from schemas.assistant import AssistantSchema
from services.assistant_service import AssistantService

router = APIRouter(tags=["assistants"])


@router.get("/", response_model=list[AssistantSchema])
async def get_all_assistants(
    request: Request,  # Добавляем request
    assistant_service: Annotated[AssistantService, Depends(get_assistant_service)],
):
    base_url = str(request.base_url)  # Получаем "http://127.0.0.1:8000/"

    assistants = await assistant_service.get_all_assistants()
    for assistant in assistants:
        assistant.photo = f"{base_url}{assistant.photo}"  # Добавляем base_url к относительному пути

    return assistants

