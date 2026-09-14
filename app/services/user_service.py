from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BusinessException,
    ConflictException,
    NotFoundException,
)
from app.core.security import hash_password
from app.models.enums import UserRole, UserStatus
from app.models.specialty import Specialty
from app.models.user import (
    Admin,
    Doctor,
    Patient,
    Receptionist,
    User,
)
from app.schemas.user import (
    UserCreate,
    UserUpdate,
)


class UserService:

    @staticmethod
    def create_user(
        db: Session,
        data: UserCreate,
    ) -> User:

        if data.role == UserRole.ADMIN:
            raise BusinessException(
                "Khong the tao tai khoan Admin tai day"
            )

        existing_username = db.execute(
            select(User).where(
                User.username == data.username
            )
        ).scalar_one_or_none()

        if existing_username is not None:
            raise ConflictException(
                "Username da ton tai"
            )

        if data.email is not None:
            existing_email = db.execute(
                select(User).where(
                    User.email == data.email
                )
            ).scalar_one_or_none()

            if existing_email is not None:
                raise ConflictException(
                    "Email da ton tai"
                )

        if data.phone is not None:
            existing_phone = db.execute(
                select(User).where(
                    User.phone == data.phone
                )
            ).scalar_one_or_none()

            if existing_phone is not None:
                raise ConflictException(
                    "SĐT da ton tai"
                )

        password_hash = hash_password(
            data.password
        )

        if data.role == UserRole.DOCTOR:

            if data.specialty_id is None:
                raise BusinessException(
                    "Doctor phai co specialty_id"
                )

            specialty = db.get(
                Specialty,
                data.specialty_id,
            )

            if specialty is None:
                raise NotFoundException(
                    "Khong tim thay chuyen khoa"
                )

            user = Doctor(
                username=data.username,
                password=password_hash,
                full_name=data.full_name,
                email=data.email,
                phone=data.phone,
                gender=data.gender,
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
                gender=data.gender,
                role=UserRole.RECEPTIONIST,
                status=UserStatus.ACTIVE,
                type="receptionist",
            )

        elif data.role == UserRole.PATIENT:

            user = Patient(
                username=data.username,
                password=password_hash,
                full_name=data.full_name,
                email=data.email,
                phone=data.phone,
                gender=data.gender,
                role=UserRole.PATIENT,
                status=UserStatus.ACTIVE,
                type="patient",
                dob=data.dob,
                address=data.address,
            )

        else:
            raise BusinessException(
                "Vai tro khong hop le"
            )

        try:
            db.add(user)
            db.commit()
            db.refresh(user)

            return user

        except IntegrityError as exc:
            db.rollback()

            raise ConflictException(
                "Du lieu bi trung"
            ) from exc

    @staticmethod
    def get_all_users(
        db: Session,
        role: UserRole | None = None,
    ) -> list[User]:

        stmt = (
            select(User)
            .where(
                User.role != UserRole.ADMIN
            )
            .order_by(
                User.created_at.desc()
            )
        )

        if role is not None:

            if role == UserRole.ADMIN:
                return []

            stmt = stmt.where(
                User.role == role
            )

        return db.execute(
            stmt
        ).scalars().all()

    @staticmethod
    def get_user_by_id(
        db: Session,
        user_id: int,
    ) -> User:

        user = db.get(
            User,
            user_id,
        )

        if user is None:
            raise NotFoundException(
                "Khong tim thay nguoi dung"
            )

        if user.role == UserRole.ADMIN:
            raise NotFoundException(
                "Khong tim thay nguoi dung"
            )

        return user

    @staticmethod
    def update_user(
        db: Session,
        user: User,
        data: UserUpdate,
    ) -> User:

        update_data = data.model_dump(
            exclude_unset=True
        )

        if "email" in update_data:
            email = update_data["email"]

            if email != user.email:

                existing = db.execute(
                    select(User)
                    .where(
                        User.email == email,
                        User.user_id != user.user_id,
                    )
                ).scalar_one_or_none()

                if existing is not None:
                    raise ConflictException(
                        "Email da ton tai"
                    )

        if "phone" in update_data:
            phone = update_data["phone"]

            if phone != user.phone:

                existing = db.execute(
                    select(User)
                    .where(
                        User.phone == phone,
                        User.user_id != user.user_id,
                    )
                ).scalar_one_or_none()

                if existing is not None:
                    raise ConflictException(
                        "SĐT da ton tai"
                    )

        if "password" in update_data:

            new_password = update_data.pop(
                "password"
            )

            if new_password:
                user.password = hash_password(
                    new_password
                )

        if (
            user.role == UserRole.DOCTOR
            and "specialty_id" in update_data
        ):

            specialty_id = update_data[
                "specialty_id"
            ]

            specialty = db.get(
                Specialty,
                specialty_id,
            )

            if specialty is None:
                raise NotFoundException(
                    "Khong tim thay chuyen khoa"
                )

        for field, value in update_data.items():

            if hasattr(user, field):
                setattr(
                    user,
                    field,
                    value,
                )

        try:
            db.commit()
            db.refresh(user)

            return user

        except IntegrityError as exc:
            db.rollback()

            raise ConflictException(
                "Du lieu bi trung"
            ) from exc

    @staticmethod
    def update_status(
        db: Session,
        user: User,
        status: UserStatus,
        current_user_id: int,
    ) -> User:

        if user.user_id == current_user_id:

            raise BusinessException(
                "Khong the tu khoa hoac thay doi trang thai tai khoan cua minh"
            )

        if user.role == UserRole.ADMIN:

            raise BusinessException(
                "Khong the thay doi trang thai tai khoan Admin"
            )

        user.status = status

        db.commit()
        db.refresh(user)

        return user