from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedException
from app.core.security import create_access_token, verify_password
from app.models.enums import UserStatus
from app. models.user import User

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