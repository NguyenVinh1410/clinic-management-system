from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class PrescriptionDetailCreate(BaseModel):

    medicine_id: int = Field(gt=0)

    quantity: int = Field(gt=0)

    dosage: str = Field(
        min_length=1,
        max_length=255,
    )

    usage_note: str | None = Field(
        default=None,
        max_length=500
    )

class PrescriptionCreate(BaseModel):
    record_id: int = Field(gt=0)

    details: list[PrescriptionDetailCreate] = Field(min_length=1)

class PrescriptionDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    prescription_id: int
    medicine_id: int

    quantity: int
    dosage: str
    usage_note: str | None

class PrescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prescription_id: int

    record_id: int

    created_at: datetime

    details: list[PrescriptionDetailResponse]