from datetime import datetime

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.base import Base
from app.models.enums import AppointmentCreatedBy, AppointmentStatus

class Appointment(Base):
    __tablename__ = "appointment"

    appointment_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    schedule_id: Mapped[int] = mapped_column(
        ForeignKey(
            "working_schedule.schedule_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey(
            "patient.user_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    chat_session_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "chat_session.session_id",
            ondelete="SET NULL",
        ),
        nullable=True,
        unique=True,
        index=True,
    )

    appointment_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    status: Mapped[AppointmentStatus] = mapped_column(
        SQLEnum(
            AppointmentStatus,
            name="appointment_status",
        ),
        nullable=False,
        default=AppointmentStatus.PENDING,
        server_default=AppointmentStatus.PENDING.value,
    )

    created_by: Mapped[AppointmentCreatedBy] = mapped_column(
        SQLEnum(
            AppointmentCreatedBy,
            name="appointment_create_by",
        ),
        nullable=False,
    )

    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    schedule = relationship(
        "WorkingSchedule",
        back_populates="appointment",
    )

    patient = relationship(
        "Patient",
        back_populates="appointment",
    )

    chat_session = relationship(
        "ChatSession",
        back_populates="appointment",
        uselist=False,
    )

    medical_record = relationship(
        "MedicalRecord",
        back_populates="appointment",
        uselist=False,
    )

    invoice = relationship(
        "Invoice",
        back_populates="appointment",
        uselist=False,
    )

    @property
    def doctor_id(self) -> int:
        return self.schedule.doctor.user_id

    @property
    def doctor_name(self) -> str:
        return self.schedule.doctor.full_name

    @property
    def specialty_id(self) -> int:
        return self.schedule.doctor.specialty_id

    @property
    def specialty_name(self) -> str:
        return (
            self.schedule.doctor.specialty.name
            if self.schedule.doctor.specialty is not None
            else ""
        )

    @property
    def patient_name(self) -> str:
        return self.patient.full_name

    @property
    def patient_phone(self) -> str | None:
        return self.patient.phone