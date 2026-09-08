from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException
from app.models.enums import MedicineStatus
from app.models.medicine import Medicine
from app.schemas.medicine import MedicineCreate, MedicineUpdate

class MedicineService:

    @staticmethod
    def get_medicine_by_id(
            db: Session,
            medicine_id: int
    ) -> Medicine:

        medicine = db.get(Medicine, medicine_id)

        if medicine is None:
            raise NotFoundException("Khong tim thay thuoc")

        return medicine

    @staticmethod
    def get_all_medicines(db: Session) -> list[Medicine]:

        stmt = (
            select(Medicine)
            .order_by(Medicine.name)
        )

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def create_medicine(
            db: Session,
            data: MedicineCreate
    ) -> Medicine:

        name = data.name.strip()
        unit = data.unit.strip()

        stmt = (
            select(Medicine)
            .where(Medicine.name == name)
        )

        existing = db.execute(stmt).scalar_one_or_none()

        if existing is not None:
            raise ConflictException("Thuoc da ton tai")

        medicine = Medicine(
            name=name,
            unit=unit,
            price=data.price,
            stock_qty=data.stock_qty,
            status=data.status,
        )

        try:
            db.add(medicine)
            db.commit()
            db.refresh(medicine)

            return medicine

        except IntegrityError as exc:
            db.rollback()
            raise ConflictException("Khong the tao thuoc") from exc

    @staticmethod
    def update_medicine(
            db: Session,
            medicine: Medicine,
            data: MedicineUpdate
    ) -> Medicine:

        update_data = data.model_dump(exclude_unset=True)

        name = update_data.get("name")

        if name is not None:
            name = name.strip()

            stmt = (
                select(Medicine)
                .where(
                    Medicine.name == name,
                    Medicine.medicine_id != medicine.medicine_id,
                )
            )

            existing = db.execute(stmt).scalar_one_or_none()

            if existing is not None:
                raise ConflictException("Ten thuoc da ton tai")

            update_data["name"] = name

        unit = update_data.get("unit")

        if unit is not None:
            update_data["unit"] = unit.strip()

        stock_qty = update_data.get("stock_qty")

        if stock_qty is not None and stock_qty < 0:
            raise ConflictException("Ton kho khong duoc am")

        for field, value in update_data.items():
            setattr(medicine, field, value)

        try:
            db.commit()
            db.refresh(medicine)

            return medicine

        except IntegrityError as exc:
            db.rollback()
            raise ConflictException("Khong the cap nhat thuoc") from exc

    @staticmethod
    def discontinue_medicine(
            db: Session,
            medicine: Medicine
    ) -> Medicine:

        medicine.status = MedicineStatus.DISCONTINUED

        db.commit()
        db.refresh(medicine)

        return medicine
