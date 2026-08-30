from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from pwdlib import PasswordHash

from app.config.settings import  settings

password_hash = PasswordHash.recommended()

def hash_password(plain_password: str) -> str:
    #hash pw truoc khi luu vao database
    return password_hash.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    #kiem tra nguoi dung co khop voi pw hash trong database khong
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(user_id: int, expires_delta: timedelta | None=None) -> str:
    #tao JWT access token, subject thuong la user_id
    now = datetime.now(timezone.utc)

    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.jwt_expire_minutes)

    expire = now + expires_delta

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expire,
    }

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> dict:
    #JWT kh hop le thi phat sinh JWTError
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None