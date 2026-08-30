from decimal import Decimal

from sqlalchemy import Enum as SQLEnum, Numeric, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.base import Base
from app.models.enums import MedicineStatus

class Medicine(Base):
    __tablename__ = "medicine"

    medicine_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    stock_qty: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
        server_default="0",
    )

    status: Mapped[MedicineStatus] = mapped_column(
        SQLEnum(
            MedicineStatus,
            name="medicine_status",
        ),
        nullable=False,
        default=MedicineStatus.ACTIVE,
        server_default=MedicineStatus.ACTIVE.value,
    )

    prescription_details = relationship(
        "PrescriptionDetail",
        back_populates="medicine",
    )