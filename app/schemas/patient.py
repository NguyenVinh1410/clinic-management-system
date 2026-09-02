from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Gender, UserStatus, UserRole

class PatientResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    user_id: int
    username: str
    full_name: str
    email: str | None
    phone: str | None
    gender: Gender | None
    role: UserRole
    status: UserStatus
    created_at: datetime

    dob: date | None
    address: str | None

class PatientUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length= 1,
        max_length= 100,
    )

    email: str | None = Field(
        default=None,
        max_length= 255,
    )

    phone: str | None = Field(
        default=None,
        min_length= 9,
        max_length= 20,
    )

    dob: date | None = None

    gender: Gender | None = None

    address: str | None = Field(
        default=None,
        max_length= 255,
    )

