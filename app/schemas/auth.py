from datetime import datetime, date

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import UserRole, UserStatus, Gender

class LoginRequest(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=50,
    )
    password: str = Field(
        min_length=1,
        max_length=255,
    )

class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=6,
        max_length=50,
    )

    password: str = Field(
        min_length=6,
        max_length=255,
    )

    confirm_password: str = Field(
        min_length=6,
        max_length=255,
    )

    full_name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: str | None = Field(
        default=None,
        max_length=100,
    )

    phone: str | None = Field(
        default=None,
        min_length=9,
        max_length=20,
    )

    dob: date | None = None

    gender: Gender | None = None

    address: str | None = Field(
        default=None,
        max_length=255,
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip()

        if not any(
            char.isalpha()
            for char in value
        ):
            raise ValueError("Username phai co it nhat 1 chu cai")

        if not any(
                char.isdigit()
                for char in value
        ):
            raise ValueError(
                "Username phai co it nhat 1 chu so"
            )

        if not all(
                char.isalnum() or char == "_"
                for char in value
        ):
            raise ValueError(
                "Username chi duoc chua chu, so va dau gach duoi"
            )

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:

        if not any(
                char.isdigit()
                for char in value
        ):
            raise ValueError(
                "Password phai co it nhat 1 chu so"
            )

        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:

        if value is None:
            return None

        value = value.strip()

        if value == "":
            return None

        if "@" not in value:
            raise ValueError(
                "Email khong hop le"
            )

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:

        if value is None:
            return None

        value = value.strip()

        if not value.isdigit():
            raise ValueError(
                "SĐT chi duoc chua chu so"
            )

        return value

    @model_validator(mode="after")
    def validate_confirm_password(self):

        if self.password != self.confirm_password:
            raise ValueError(
                "Password xac nhan khong khop"
            )

        return self

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    user_id: int
    username: str
    full_name: str
    email: str | None
    phone: str | None
    role: UserRole
    status: UserStatus
    created_at: datetime