from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.core.security import decode_access_token
from app.models import User
from app.models.enums import UserRole, UserStatus

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedException("Token khong hop le hoac het han")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Token khong ton tai")

    user = db.get(User, int(user_id))
    if user is None:
        raise UnauthorizedException("Nguoi dung khong ton tai")

    if user.status != UserStatus.ACTIVE:
        raise UnauthorizedException("Tai khoan bi khoa")

    return user

def requires_role(*allowed_roles: UserRole):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenException("Khong co quyen truy cap")
        return current_user
    return dependency
