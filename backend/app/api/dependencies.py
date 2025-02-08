import hashlib
from typing import Annotated

from fastapi import Depends, HTTPException, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from models import db_helper
from services import ChatService
from services.assistant_service import AssistantService
from services.user_service import UserService


async def get_assistant_service(
        db_session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    return AssistantService(db_session)


async def get_chat_service(
        db_session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    return ChatService(db_session)


async def get_user_service(
        db_session: Annotated[AsyncSession, Depends(db_helper.session_getter)]
):
    return UserService(db_session)


SECRET_KEY = settings.openai.secret_hash_key


def generate_hash(user_id: str, secret_key: str) -> str:
    data = f"{user_id}:{secret_key}"
    return hashlib.sha256(data.encode()).hexdigest()


async def verify_user(
    db_session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    user_external_id: str = Header(None),
    hash: str = Header(None),
):
    if not user_external_id or not hash:
        raise HTTPException(status_code=400, detail="Missing headers")

    expected_hash = generate_hash(user_external_id, SECRET_KEY)

    if hash != expected_hash:
        raise HTTPException(status_code=403, detail="Invalid credentials")

    user_service = UserService(db_session)
    user = await user_service.get_user_by_external_id(int(user_external_id))
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user.id


async def verify_user_ws(
    db_session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    user_external_id: str = Query(None),
    hash: str = Query(None),
):
    if not user_external_id or not hash:
        raise HTTPException(status_code=400, detail="Missing query parameters")

    expected_hash = generate_hash(user_external_id, SECRET_KEY)

    if hash != expected_hash:
        raise HTTPException(status_code=403, detail="Invalid credentials")

    user_service = UserService(db_session)
    user = await user_service.get_user_by_external_id(int(user_external_id))
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user.id
