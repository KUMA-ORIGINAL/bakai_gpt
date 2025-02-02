from datetime import datetime

from pydantic import BaseModel


class MessageSchema(BaseModel):
    id: int
    sender: str
    content: str
    created_at: datetime
    chat_id: int  # Foreign key to Chat

    class Config:
        from_attributes = True
