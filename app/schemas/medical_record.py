from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class MedicalRecordCreate(BaseModel):
    appointment_id: int = Field(gt=0)

    symptoms: str | None = Field(
        default=None,
        max_length=5000
    )

    diagnosis: str = Field(
        min_length=1,
        max_length=5000,
    )

    note: str | None = Field(
        default=None,
        max_length=5000,
    )

    examined_at: datetime

class MedicalRecordUpdate(BaseModel):
    symptoms: str | None = Field(
        default=None,
        max_length=5000,
    )

    diagnosis: str | None = Field(
        default=None,
        min_length=1,
        max_length=5000,
    )

    note: str | None = Field(
        default=None,
        max_length=5000,
    )

class MedicalRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    record_id: int

    appointment_id: int

    symptoms: str | None

    diagnosis: str

    note: str | None

    examined_at: datetime


