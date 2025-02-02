from pydantic import BaseModel
from pydantic import ConfigDict


class UserBaseSchema(BaseModel):
    external_id: int
    full_name: str


class UserCreateSchema(UserBaseSchema):
    pass


class UserSchema(UserBaseSchema):
    id: int

    class Config:
        from_attributes = True
