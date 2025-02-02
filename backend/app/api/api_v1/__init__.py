from fastapi import APIRouter

from config import settings

from .users import router as users_router
from .chat_ws import router as chat_ws_router
from .chat import router as chat_router
from .assistant import router as assistant_router

router = APIRouter(
    prefix=settings.api.v1.prefix,
)
router.include_router(
    users_router,
    prefix=settings.api.v1.users,
)
router.include_router(
    chat_ws_router,
    prefix=settings.ws,
)
router.include_router(
    assistant_router,
    prefix=settings.api.v1.assistants
)
router.include_router(
    chat_router,
    prefix=settings.api.v1.chats
)
