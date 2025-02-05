from pydantic import BaseModel
from pydantic import ConfigDict


class UserBaseSchema(BaseModel):
    user_external_id: int


class UserCreateSchema(UserBaseSchema):
    pass


class UserSchema(UserBaseSchema):
    id: int

    class Config:
        from_attributes = True
