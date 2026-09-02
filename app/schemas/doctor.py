from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Gender, UserRole, UserStatus

class DoctorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str
    full_name: str
    email: str | None
    phone: str | None
    gender: Gender | None
    role: UserRole
    status: UserStatus
    created_at: datetime

    qualification: str | None
    bio: str | None

    specialty_id: int

class DoctorUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    email: str | None = Field(
        default=None,
        max_length=255,
    )

    phone: str | None = Field(
        default=None,
        min_length=9,
        max_length=20,
    )

    gender: Gender | None = None

    qualification: str | None = Field(
        default=None,
        max_length=255,
    )

    bio: str | None = Field(
        default=None,
        max_length=5000,
    )

    specialty_id: int | None = Field(
        default=None,
        gt=0,
    )