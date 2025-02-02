from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models import db_helper, User, Assistant
from services.assistant_service import AssistantService
from services.user_service import UserService


async def get_current_user(
    external_id: int,
    db_session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ]
) -> User:
    user_service = UserService(db_session)
    user = await user_service.get_user_by_external_id(external_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user.id


async def get_assistant(
    assistant_id: int,
    db_session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ]
) -> Assistant:
    assistant_service = AssistantService(db_session)
    assistant = await assistant_service.get_assistant_by_id(assistant_id)
    if assistant is None:
        raise HTTPException(status_code=404, detail="Ассистент не найден")
    return assistant.id
