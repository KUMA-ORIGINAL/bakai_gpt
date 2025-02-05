from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from schemas.assistant import AssistantSchema
from schemas.message import MessageSchema
from schemas.user import UserSchema


class ChatCreateSchema(BaseModel):
    assistant_id: int


class ChatUpdateSchema(BaseModel):
    user_id: Optional[int] = None
    assistant_id: Optional[int] = None


class ChatListSchema(BaseModel):
    id: int
    name: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatSchema(BaseModel):
    id: int
    name: Optional[str] = None
    user: UserSchema
    assistant: AssistantSchema
    messages: List[MessageSchema] = []

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
