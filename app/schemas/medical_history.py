from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

class MedicalHistoryMedicineResponse(BaseModel):
    medicine_id: int

    name: str

    unit: str

    price: Decimal

    quantity: int

    dosage: str

    usage_note: str | None

class MedicalHistoryPrescriptionResponse(BaseModel):
    prescription_id: int

    created_at: datetime

    medicines: list[MedicalHistoryMedicineResponse]

class MedicalHistoryItemResponse(BaseModel):
    appointment_id: int

    appointment_time: datetime

    doctor_id: int

    doctor_name: str

    specialty_id: int | None

    specialty_name: str | None

    examined_at: datetime | None

    symptoms: str | None

    diagnosis: str | None

    note: str | None

    prescription: MedicalHistoryPrescriptionResponse | None

class MedicalHistoryResponse(BaseModel):
    items: list[MedicalHistoryItemResponse]