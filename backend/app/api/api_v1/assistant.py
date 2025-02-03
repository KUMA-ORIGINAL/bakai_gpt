from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import get_assistant_service
from schemas.assistant import AssistantSchema
from services.assistant_service import AssistantService

router = APIRouter(tags=["assistants"])


@router.get("/", response_model=list[AssistantSchema])
async def get_all_assistants(
    assistant_service: Annotated[AssistantService, Depends(get_assistant_service)],
):
    return await assistant_service.get_all_assistants()

