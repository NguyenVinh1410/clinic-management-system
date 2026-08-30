from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Numeric
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.base import Base
from app.models.enums import InvoiceStatus, PaymentMethod

class Invoice(Base):
    __tablename__ = "invoice"

    invoice_id: Mapped[int] = mapped_column(
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

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    status: Mapped[InvoiceStatus] = mapped_column(
        SQLEnum(
            InvoiceStatus,
            name="invoice_status",
        ),
        nullable=False,
        default=InvoiceStatus.UNPAID,
        server_default=InvoiceStatus.UNPAID.value,
    )

    payment_method: Mapped[PaymentMethod | None] = mapped_column(
        SQLEnum(
            PaymentMethod,
            name="payment_method",
        ),
        nullable=True,
    )

    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    appointment = relationship(
        "Appointment",
        back_populates="invoice",
    )

    