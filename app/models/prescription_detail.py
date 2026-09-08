from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.base import Base

class PrescriptionDetail(Base):
    __tablename__ = "prescription_detail"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    prescription_id: Mapped[int] = mapped_column(
        ForeignKey(
            "prescription.prescription_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    medicine_id: Mapped[int] = mapped_column(
        ForeignKey(
            "medicine.medicine_id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    dosage: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    usage_note: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    prescription = relationship(
        "Prescription",
        back_populates="details",
    )

    medicine = relationship(
        "Medicine",
        back_populates="prescription_details",
    )

    __table_args__ = (
        UniqueConstraint(
            "prescription_id",
            "medicine_id",
            name="uq_prescription_medicine",
        ),
    )