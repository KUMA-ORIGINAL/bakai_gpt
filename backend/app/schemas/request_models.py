from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    assistant_type: Optional[str] = 'default'  # Тип ассистента (опционально)

    class Config:
        from_attributes = True
