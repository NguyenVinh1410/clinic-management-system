from datetime import date, time
from typing import Literal

from pydantic import BaseModel, Field


AIIntentName = Literal[
    "greeting",
    "find_doctor",
    "find_specialty",
    "working_hours",
    "find_available_slots",
    "book_appointment",
    "cancel_appointment",
    "my_appointments",
    "process_guidance",
    "unknown",
]


class AICommand(BaseModel):

    intent: AIIntentName = Field(
        description="Intent cua nguoi dung"
    )

    doctor_name: str | None = Field(
        default=None,
        description="Ten bac si neu nguoi dung nhac den"
    )

    specialty_name: str | None = Field(
        default=None,
        description="Ten chuyen khoa neu nguoi dung nhac den"
    )

    appointment_date: date | None = Field(
        default=None,
        description="Ngay kham neu nguoi dung cung cap"
    )

    appointment_time: time | None = Field(
        default=None,
        description="Gio kham neu nguoi dung cung cap"
    )

    appointment_id: int | None = Field(
        default=None,
        description="Ma lich hen neu nguoi dung cung cap"
    )