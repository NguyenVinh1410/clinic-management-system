from datetime import datetime, date

from sqlalchemy import DateTime, Date, Enum as SQLEnum, String, func, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import  Base
from app.models.enums import UserRole, UserStatus, PatientGender


class User(Base):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
    )

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(
            UserRole,
            name="user_role",
        ),
        nullable=False,
    )

    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(
            UserStatus,
            name="user_status",
        ),
        nullable=False,
        default=UserStatus.ACTIVE,
        server_default=UserStatus.ACTIVE.value,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "user",
    }

class Admin(User):
    __tablename__ = "admin"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.user_id", ondelete="CASCADE"),
        primary_key=True,
    )

    __mapper_args__ = {
        "polymorphic_identity": "admin",
    }

class Receptionist(User):
    __tablename__ = "receptionist"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.user_id", ondelete="CASCADE"),
        primary_key=True,
    )

    __mapper_args__ = {
        "polymorphic_identity": "receptionist",
    }

class Doctor(User):
    __tablename__ = "doctor"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.user_id", ondelete="CASCADE"),
        primary_key=True,
    )

    qualification: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    specialty_id: Mapped[int] = mapped_column(
        ForeignKey("specialty.specialty_id", ondelete="RESTRICT"),
        nullable=False,
    )

    specialty = relationship(
        "Specialty",
        back_populates="doctor",
    )

    working_schedule = relationship(
        "WorkingSchedule",
        back_populates="doctor",
    )

    __mapper_args__ = {
        "polymorphic_identity": "doctor",
    }

class Patient(User):
    __tablename__ = "patient"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.user_id", ondelete="CASCADE"),
        primary_key=True,
    )

    dob: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    gender: Mapped[PatientGender | None] = mapped_column(
        SQLEnum(
            PatientGender,
            name="patient_gender",
        ),
        nullable=True,
    )

    address: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    appointment = relationship(
        "Appointment",
        back_populates="patient",
    )

    chat_session = relationship(
        "ChatSession",
        back_populates="patient",
        cascade="all, delete-orphan",
    )

    __mapper_args__ = {
        "polymorphic_identity": "patient",
    }
