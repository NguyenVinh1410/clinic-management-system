from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatSessionResponse(BaseModel):
    session_id: int
    patient_id: int
    started_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ChatMessageCreate(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=2000,
    )

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Nội dung tin nhắn không được để trống"
            )

        return value


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