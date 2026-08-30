from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.base import Base

class MedicalRecord(Base):
    __tablename__ = "medical_record"

    record_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    appointment_id: Mapped[int] = mapped_column(
        ForeignKey(
            "appointment.appointment_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        unique=True,
    )

    symptoms: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    diagnosis: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    examined_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    appointment = relationship(
        "Appointment",
        back_populates="medical_record",
    )

    prescription = relationship(
        "Prescription",
        back_populates="medical_record",
        uselist=False,
        cascade="all, delete-orphan",
    )