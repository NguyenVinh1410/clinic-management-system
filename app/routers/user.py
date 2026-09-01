from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, requires_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(
    prefix="/api/users",
    tags=["User Management"],
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserCreate,
    _: Annotated[
        User,
        Depends(
            requires_role(
                UserRole.ADMIN
            )
        ),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):

    return UserService.create_user(
        db=db,
        data=data,
    )