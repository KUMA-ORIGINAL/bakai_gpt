from pydantic import BaseModel


class MessageToChannelSchema(BaseModel):
    user_id: str
    message: str
    channel_id: str
