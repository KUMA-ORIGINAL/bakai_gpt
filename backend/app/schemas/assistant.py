from pydantic import BaseModel, HttpUrl


class AssistantSchema(BaseModel):
    id: int
    name: str
    description: str | None
    photo: HttpUrl

    class Config:
        from_attributes = True
