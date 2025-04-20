from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import get_assistant_service
from schemas.assistant import AssistantSchema
from services.assistant_service import AssistantService

from config import settings

router = APIRouter(tags=["assistants"])


@router.get("/", response_model=list[AssistantSchema])
async def get_all_assistants(
    assistant_service: Annotated[AssistantService, Depends(get_assistant_service)],
):
    assistants = await assistant_service.get_all_assistants()
    for assistant in assistants:
        assistant.photo = f"{settings.BASE_URL}{assistant.photo}"

    return assistants
