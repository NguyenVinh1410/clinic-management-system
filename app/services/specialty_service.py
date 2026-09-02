from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException
from app.models import Doctor
from app.models.specialty import Specialty

class SpecialtyService:

    @staticmethod
    def create_specialty(
            db: Session,
            name: str,
            description: str | None
    ) -> Specialty:

        name = name.strip()

        stmt = (
            select(Specialty)
            .where(Specialty.name == name)
        )

        existing_specialty = db.execute(stmt).scalar_one_or_none()

        if existing_specialty is not None:
            raise ConflictException("Chuyen khoa da ton tai")

        specialty = Specialty(
            name=name,
            description=description
        )

        try:
            db.add(specialty)
            db.commit()
            db.refresh(specialty)

            return specialty

        except IntegrityError as exc:
            db.rollback()

            raise ConflictException("Ten chuyen khoa da ton tai") from exc

    @staticmethod
    def get_all_specialties(
            db: Session,
    ) -> list[Specialty]:

        stmt = (
            select(Specialty)
            .order_by(Specialty.name)
        )

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def get_specialty_by_id(
            db: Session,
            specialty_id: int
    ) -> Specialty:

        stmt = (
            select(Specialty)
            .where(Specialty.specialty_id == specialty_id)
        )

        specialty = db.execute(stmt).scalar_one_or_none()

        if specialty is None:
            raise NotFoundException("Khong tim thay  chuyen khoa")

        return specialty

    @staticmethod
    def update_specialty(
            db: Session,
            specialty: Specialty,
            data: dict
    ) -> Specialty:

        name = data.get("name")

        if name is not None:

            name = name.strip()

            stmt = (
                select(Specialty)
                .where(
                    Specialty.name == name,
                    Specialty.specialty_id != specialty.specialty_id
                )
            )

            existing_specialty = db.execute(stmt).scalar_one_or_none()

            if existing_specialty is not None:
                raise ConflictException("Chuyen khoa da ton tai")

            data["name"] = name

        allowed_fields = {
            "name",
            "description",
        }

        for field, value in data.items():

            if field not in allowed_fields:
                continue

            setattr(specialty, field, value)

        try:
            db.commit()
            db.refresh(specialty)

            return specialty

        except IntegrityError as exc:
            db.rollback()
            raise ConflictException("Khong the cap nhat chuyen khoa") from exc

    @staticmethod
    def delete_specialty(
            db: Session,
            specialty_id: int
    ) -> None:

        stmt = (
            select(Specialty)
            .where(Specialty.specialty_id == specialty_id)
        )

        specialty = db.execute(stmt).scalar_one_or_none()

        if specialty is None:
            raise NotFoundException("Khong tim thay chuyen khoa")

        doctor_stmt = (
            select(Doctor)
            .where(Doctor.specialty_id == specialty_id)
            .limit(1)
        )

        doctor = (db.execute(doctor_stmt).scalar_one_or_none())

        if doctor is not None:
            raise NotFoundException("Khong the xoa")

        try:
            db.delete(specialty)
            db.commit()

        except IntegrityError as exc:
            db.rollback()

            raise ConflictException("Khong the xoa") from exc