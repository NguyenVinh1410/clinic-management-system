from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import InvoiceStatus, PaymentMethod

class InvoiceCreate(BaseModel):
    appointment_id: int = Field(gt=0)

class InvoicePaymentRequest(BaseModel):
    payment_method: PaymentMethod

class InvoicePatientInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    patient_id: int
    full_name: str
    phone: str | None = None

class InvoiceDoctorInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    doctor_id: int
    full_name: str

class InvoiceSpecialtyInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    specialty_id: int
    name: str

class InvoiceMedicineItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    medicine_id: int
    medicine_name: str
    unit: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    dosage: str
    usage_note: str | None = None

class InvoiceResponse(BaseModel):
    invoice_id: int
    appointment_id: int
    appointment_time: datetime

    patient: InvoicePatientInfo
    doctor: InvoiceDoctorInfo
    specialty: InvoiceSpecialtyInfo

    medicines: list[InvoiceMedicineItem] = []

    consultation_fee: Decimal
    medicine_total: Decimal
    total_amount: Decimal

    status: InvoiceStatus
    payment_method: PaymentMethod | None
    paid_at: datetime | None