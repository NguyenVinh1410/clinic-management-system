from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AppointmentStatus, AppointmentCreatedBy

class AppointmentCreate(BaseModel):
    schedule_id: int = Field(gt=0)

    patient_id: int | None = Field(
        default=None,
        gt=0
    )

    appointment_time: datetime

    note: str | None = Field(
        default=None,
        max_length=1000,
    )

class AppointmentUpdate(BaseModel):
    appointment_time: datetime | None = None

    note: str | None = Field(
        default=None,
        max_length=1000,
    )

class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus

class AppointmentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    appointment_id: int

    schedule_id: int

    patient_id: int

    chat_session_id: int | None

    appointment_time: datetime

    status: AppointmentStatus

    created_by: AppointmentCreatedBy

    note: str | None

    doctor_id: int

    doctor_name: str

    specialty_id: int

    specialty_name: str