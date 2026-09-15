from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import UserRole, UserStatus, Gender


class UserCreate(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=50,
    )

    password: str = Field(
        min_length=1,
        max_length=255,
    )

    full_name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: str | None = Field(
        default=None,
        max_length=255,
    )

    phone: str | None = Field(
        default=None,
        min_length=9,
        max_length=20,
    )

    gender: Gender | None = None

    role: UserRole

    # Doctor
    specialty_id: int | None = Field(
        default=None,
    )

    qualification: str | None = Field(
        default=None,
        max_length=255,
    )

    bio: str | None = Field(
        default=None,
        max_length=5000,
    )

    # Patient
    dob: date | None = None

    address: str | None = Field(
        default=None,
        max_length=255,
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 6:
            raise ValueError(
                "Username phai co it nhat 6 ky tu"
            )

        if not any(char.isalpha() for char in value):
            raise ValueError(
                "Username phai co it nhat 1 chu cai"
            )

        if not any(char.isdigit() for char in value):
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
        if len(value) < 6:
            raise ValueError(
                "Password phai co it nhat 6 ky tu"
            )

        if not any(char.isdigit() for char in value):
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
            raise ValueError("Email khong hop le")

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if value == "":
            return None

        if not value.isdigit():
            raise ValueError(
                "SĐT chi duoc chua so"
            )

        return value

    @model_validator(mode="after")
    def validate_role_specific_fields(self):
        if (
                self.role == UserRole.DOCTOR
                and (
                self.specialty_id is None
                or self.specialty_id <= 0
        )
        ):
            raise ValueError(
                "Bác sĩ phải chọn chuyên khoa"
            )

        return self


class UserUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    password: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    email: str | None = Field(
        default=None,
        max_length=255,
    )

    phone: str | None = Field(
        default=None,
        min_length=9,
        max_length=20,
    )

    gender: Gender | None = None

    # Doctor
    specialty_id: int | None = Field(
        default=None,
    )

    qualification: str | None = Field(
        default=None,
        max_length=255,
    )

    bio: str | None = Field(
        default=None,
        max_length=5000,
    )

    # Patient
    dob: date | None = None

    address: str | None = Field(
        default=None,
        max_length=255,
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str | None) -> str | None:
        if value is None:
            return None

        if value == "":
            return None

        if len(value) < 6:
            raise ValueError(
                "Password phai co it nhat 6 ky tu"
            )

        if not any(char.isdigit() for char in value):
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
            raise ValueError("Email khong hop le")

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if value == "":
            return None

        if not value.isdigit():
            raise ValueError(
                "SĐT chi duoc chua so"
            )

        return value

    @model_validator(mode="after")
    def validate_role_specific_fields(self):
        if (
                self.role == UserRole.DOCTOR
                and (
                self.specialty_id is None
                or self.specialty_id <= 0
        )
        ):
            raise ValueError(
                "Bác sĩ phải chọn chuyên khoa"
            )

        return self


class UserStatusUpdate(BaseModel):
    status: UserStatus


class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    user_id: int
    username: str
    full_name: str
    email: str | None
    phone: str | None
    gender: Gender | None

    role: UserRole
    status: UserStatus

    specialty_id: int | None = None
    qualification: str | None = None
    bio: str | None = None

    dob: date | None = None
    address: str | None = None