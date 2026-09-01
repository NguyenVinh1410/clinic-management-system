from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException, ConflictException
from app.core.security import hash_password
from app.models.enums import UserRole, UserStatus
from app.models.user import User, Doctor, Patient, Receptionist, Admin
from app.schemas.user import UserCreate


class UserService:

    @staticmethod
    def create_user(db: Session, data: UserCreate) -> User:
        stmt = (
            select(User)
            .where(User.username == data.username)
        )

        existing_username = (
            db.execute(stmt)
            .scalar_one_or_none()
        )

        if existing_username is not None:
            raise ConflictException(
                "Username da ton tai"
            )

        if data.email is not None:

            stmt = (
                select(User)
                .where(User.email == data.email)
            )

            existing_email = (
                db.execute(stmt)
                .scalar_one_or_none()
            )

            if existing_email is not None:
                raise ConflictException(
                    "Email da ton tai"
                )

        if data.phone is not None:

            stmt = (
                select(User)
                .where(User.phone == data.phone)
            )

            existing_phone = (
                db.execute(stmt)
                .scalar_one_or_none()
            )

            if existing_phone is not None:
                raise ConflictException(
                    "SĐT da ton tai"
                )

        password_hash = hash_password(data.password)

        if data.role == UserRole.DOCTOR:

            if data.specialty_id is None:
                raise BusinessException(
                    "Doctor phai co specialty_id"
                )

            user = Doctor(
                username=data.username,
                password=password_hash,
                full_name=data.full_name,
                email=data.email,
                phone=data.phone,

                role=UserRole.DOCTOR,
                status=UserStatus.ACTIVE,
                type="doctor",

                specialty_id=data.specialty_id,
                qualification=data.qualification,
                bio=data.bio,
            )

        elif data.role == UserRole.RECEPTIONIST:

            user = Receptionist(
                username=data.username,
                password=password_hash,
                full_name=data.full_name,
                email=data.email,
                phone=data.phone,

                role=UserRole.RECEPTIONIST,
                status=UserStatus.ACTIVE,
                type="receptionist",
            )

        elif data.role == UserRole.PATIENT:

            patient_dob = None

            if data.dob:
                try:
                    patient_dob = date.fromisoformat(
                        data.dob
                    )
                except ValueError as exc:
                    raise BusinessException(
                        "Ngay sinh khong hop le"
                    ) from exc

            user = Patient(
                username=data.username,
                password=password_hash,
                full_name=data.full_name,
                email=data.email,
                phone=data.phone,

                role=UserRole.PATIENT,
                status=UserStatus.ACTIVE,
                type="patient",

                dob=patient_dob,
                gender=data.gender,
                address=data.address,
            )

        else:
            user = Admin(
                username=data.username,
                password=password_hash,
                full_name=data.full_name,
                email=data.email,
                phone=data.phone,

                role=UserRole.RECEPTIONIST,
                status=UserStatus.ACTIVE,
                type="admin",
            )

        try:
            db.add(user)
            db.commit()
            db.refresh(user)

            return user

        except IntegrityError as exc:
            db.rollback()
            raise ConflictException("Du lieu bi trung") from exc
