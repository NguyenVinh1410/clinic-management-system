from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException
from app.models.enums import UserStatus
from app.models.specialty import Specialty
from app.models.user import User, Doctor
from app.schemas.doctor import DoctorUpdate


class DoctorService:

    @staticmethod
    def get_all_doctors(
            db: Session,
    ) -> list[Doctor]:

        stmt = (
            select(Doctor)
            .order_by(Doctor.user_id)
        )

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def get_doctor_by_id(
            db: Session,
            doctor_id: int,
    ) -> Doctor:

        stmt = (
            select(Doctor)
            .where(Doctor.user_id == doctor_id)
        )

        doctor = db.execute(stmt).scalar_one_or_none()

        if doctor is None:
            raise NotFoundException("Khong tim thay bac si")

        return doctor

    @staticmethod
    def get_specialty(
            db: Session,
            specialty_id: int,
    ) -> Specialty:

        specialty = db.get(
            Specialty,
            specialty_id
        )

        if specialty is None:
            raise NotFoundException("Khong tim thay chuyen khoa")

        return specialty

    @staticmethod
    def update_doctor(
            db: Session,
            doctor: Doctor,
            data: DoctorUpdate,
    ) -> Doctor:

        update_data = data.model_dump(exclude_unset=True)

        email = update_data.get("email")

        if email is not None:

            stmt = (
                select(User)
                .where(
                    User.email == email,
                    User.user_id != doctor.user_id,
                )
            )

            existing_email = (db.execute(stmt).scalar_one_or_none())

            if existing_email is not None:
                raise ConflictException("Email da ton tai")

        phone = update_data.get("phone")

        if phone is not None:
            stmt = (
                select(User)
                .where(
                    User.phone == phone,
                    User.user_id != doctor.user_id,
                )
            )

            existing_phone = (db.execute(stmt).scalar_one_or_none())

            if existing_phone is not None:
                raise ConflictException("SĐT da ton tai")

        specialty_id = update_data.get("specialty_id")

        if specialty_id is not None:
            DoctorService.get_specialty(
                db=db,
                specialty_id=specialty_id,
            )

        allowed_fields = {
            "full_name",
            "email",
            "phone",
            "gender",
            "qualification",
            "bio",
            "specialty_id",
        }

        for field, value in update_data.items():
            if field not in allowed_fields:
                continue

            setattr(doctor, field, value)

        try:
            db.commit()
            db.refresh(doctor)

            return doctor

        except IntegrityError as exc:

            db.rollback()

            raise ConflictException("Khong the cap nhat") from exc

    @staticmethod
    def deactivate_doctor(
            db: Session,
            doctor: Doctor,
    ) -> Doctor:

        if doctor.status == UserStatus.LOCKED:
            return doctor

        doctor.status = UserStatus.LOCKED

        db.commit()
        db.refresh(doctor)

        return doctor
