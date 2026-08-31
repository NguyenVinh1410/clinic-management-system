from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import UserRole, UserStatus

class LoginRequest(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=50,
    )
    password: str = Field(
        min_length=1,
        max_length=255,
    )

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    user_id: int
    username: str
    full_name: str
    email: str | None
    phone: str | None
    role: UserRole
    status: UserStatus
    created_at: datetime