from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import MedicineStatus

class MedicineCreate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=150,
    )

    unit: str = Field(
        min_length=1,
        max_length=50,
    )

    price: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    stock_qty: int = Field(ge=0)

    status: MedicineStatus = MedicineStatus.ACTIVE

class MedicineUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    unit: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    stock_qty: int | None = Field(
        default=None,
        ge=0,
    )

    status: MedicineStatus | None = None

class MedicineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    medicine_id: int

    name: str
    unit: str
    price: Decimal
    stock_qty: int

    status: MedicineStatus
