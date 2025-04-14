from datetime import datetime
from typing import List

from pydantic import BaseModel

from schemas.file import FileSchema


class MessageSchema(BaseModel):
    id: int
    sender: str
    content: str
    created_at: datetime
    chat_id: int
    files: List[FileSchema] = []

    class Config:
        from_attributes = True
