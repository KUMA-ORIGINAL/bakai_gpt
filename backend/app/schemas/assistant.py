from pydantic import BaseModel


class AssistantSchema(BaseModel):
    id: int
    name: str
    description: str | None

    class Config:
        from_attributes = True
