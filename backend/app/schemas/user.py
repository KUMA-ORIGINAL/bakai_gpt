from pydantic import BaseModel, Field
from pydantic import ConfigDict


class UserBaseSchema(BaseModel):
    user_external_id: int = Field(..., ge=-1, le=9223372036854775807)


class UserCreateSchema(UserBaseSchema):
    pass


class UserSchema(UserBaseSchema):
    id: int

    class Config:
        from_attributes = True
