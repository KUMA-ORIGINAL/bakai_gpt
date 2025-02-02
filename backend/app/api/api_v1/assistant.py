from fastapi import APIRouter, Depends

from services.assistant_service import AssistantService
from schemas.assistant import AssistantSchema

router = APIRouter(tags=["assistants"])


@router.get("/", response_model=list[AssistantSchema])
async def get_all_assistants(
    assistant_service: AssistantService = Depends()
):
    return await assistant_service.get_all_assistants()
