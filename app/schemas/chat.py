from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatSessionResponse(BaseModel):
    session_id: int
    patient_id: int
    started_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ChatMessageCreate(BaseModel):
    content: str


class ChatMessageResponse(BaseModel):
    message_id: int
    session_id: int
    sender_type: str
    content: str
    intent: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ChatResponse(BaseModel):
    session_id: int
    intent: str
    reply: str