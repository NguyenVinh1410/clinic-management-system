from datetime import date, time

from sqlalchemy import Date, Enum as SQLEnum, ForeignKey, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import WorkingScheduleStatus

class WorkingSchedule(Base):
    __tablename__ = 'working_schedule'

    schedule_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctor.user_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    work_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    status: Mapped[WorkingScheduleStatus] = mapped_column(
        SQLEnum(
            WorkingScheduleStatus,
            name="working_schedule_status",
        ),
        nullable=False,
        default=WorkingScheduleStatus.ACTIVE,
        server_default=WorkingScheduleStatus.ACTIVE.value,
    )

    doctor = relationship("Doctor", back_populates="working_schedule")

    appointment = relationship("Appointment", back_populates="schedule")

    __table_args__ = (
        UniqueConstraint(
            "doctor_id",
            "work_date",
            "start_time",
            "end_time",
            name="uq_doctor_working_schedule",
        ),
    )