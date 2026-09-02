from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import UnauthorizedException, ConflictException
from app.core.security import create_access_token, verify_password, hash_password
from app.models.enums import UserStatus, UserRole, Gender
from app.models.user import User, Patient
from app.schemas.auth import RegisterRequest

class AuthService:
    @staticmethod
    def authenticate_user(
            db: Session,
            username: str,
            password: str
    ) -> User:

        stmt = (
            select(User)
            .where(User.username == username)
        )

        user = db.execute(stmt).scalar_one_or_none()

        if user is None:
            raise UnauthorizedException("Sai ten dang nhap hoac mat khau!")

        if not verify_password(
            password,
            user.password,
        ):
            raise UnauthorizedException(
                "Sai ten dang nhap hoac mat khau!"
            )

        if user.status != UserStatus.ACTIVE:
            raise UnauthorizedException(
                "Tai khoan bi khoa hoac khong hoat dong"
            )

        return user

    @staticmethod
    def login(
            db: Session,
            username: str,
            password: str
    ) -> str:

        user = AuthService.authenticate_user(
            db=db,
            username=username,
            password=password
        )

        return create_access_token(
            user_id=user.user_id,
        )

    @staticmethod
    def register_patient(
            db: Session,
            data: RegisterRequest,
    ) -> Patient:

        stmt = (
            select(User)
            .where(User.username == data.username)
        )

        if db.execute(stmt).scalar_one_or_none():
            raise ConflictException(
                "Username da ton tai"
            )

        if data.email is not None:

            stmt = (
                select(User)
                .where(User.email == data.email)
            )

            if db.execute(stmt).scalar_one_or_none():
                raise ConflictException(
                    "Email da ton tai"
                )

        if data.phone is not None:

            stmt = (
                select(User)
                .where(User.phone == data.phone)
            )

            if db.execute(stmt).scalar_one_or_none():
                raise ConflictException(
                    "SĐT da ton tai"
                )

        patient = Patient(
            username=data.username,
            password=hash_password(data.password),
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

        try:

            db.add(patient)
            db.commit()
            db.refresh(patient)

            return patient

        except IntegrityError as exc:
            db.rollback()
            raise ConflictException("Du lieu bi trung") from exc
