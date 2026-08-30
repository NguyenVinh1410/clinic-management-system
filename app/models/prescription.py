from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.base import Base

class Prescription(Base):
    __tablename__ = "prescription"

    prescription_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    record_id: Mapped[int] = mapped_column(
        ForeignKey(
            "medical_record.record_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        unique=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    medical_record = relationship(
        "MedicalRecord",
        back_populates="prescription",
    )

    details = relationship(
        "PrescriptionDetail",
        back_populates="prescription",
        cascade="all, delete-orphan",
    )
