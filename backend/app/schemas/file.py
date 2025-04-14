from pydantic import BaseModel


class FileSchema(BaseModel):
    id: int
    file_id: str
    filename: str

    class Config:
        from_attributes = True
