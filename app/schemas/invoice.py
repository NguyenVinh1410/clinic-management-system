from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import InvoiceStatus, PaymentMethod

class InvoiceCreate(BaseModel):
    appointment_id: int = Field(gt=0)

class InvoicePaymentRequest(BaseModel):
    payment_method: PaymentMethod

class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    invoice_id: int

    appointment_id: int

    total_amount: Decimal

    status: InvoiceStatus

    payment_method: PaymentMethod | None

    paid_at: datetime | None