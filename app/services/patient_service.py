from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException
from app.models.user import User, Patient



class PatientService:

    @staticmethod
    def get_patient_by_id(
            db: Session,
            patient_id: int
    ) -> Patient:

        stmt = (
            select(Patient)
            .where(Patient.user_id == patient_id)
        )

        patient = db.execute(stmt).scalar_one_or_none()

        if patient is None:
            raise NotFoundException("Khong tim thay benh nhan")

        return patient

    @staticmethod
    def get_all_patients(db: Session) -> list[Patient]:
        stmt = (
            select(Patient)
            .order_by(Patient.user_id)
        )

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def update_patient(
            db: Session,
            patient: Patient,
            data: dict
    ) -> Patient:

        email = data.get("email")

        if email is not None:
            stmt = (
                select(User)
                .where(
                    User.email == email,
                    User.user_id != patient.user_id)

            )

            existing_email = db.execute(stmt).scalar_one_or_none()

            if existing_email is not None:
                raise ConflictException("Email da ton tai")

        phone = data.get("phone")

        if phone is not None:
            stmt = (
                select(User)
                .where(
                    User.phone == phone,
                    User.user_id != patient.user_id)
            )

            existing_phone = db.execute(stmt).scalar_one_or_none()

            if existing_phone is not None:
                raise ConflictException("SĐT da ton tai")

        allowed_fields = {"full_name", "email", "phone", "dob", "gender", "address"}

        for field, value in data.items():
            if field not in allowed_fields:
                continue

            setattr(patient, field, value)

        try:
            db.commit()
            db.refresh(patient)

            return patient

        except IntegrityError as exc:
            db.rollback()

            raise ConflictException("Du lieu cap nhat bi trung") from exc
