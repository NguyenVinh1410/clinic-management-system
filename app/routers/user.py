from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import (
    get_db,
    get_current_user,
    requires_role,
)
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserStatusUpdate,
    UserUpdate,
)
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


@router.get(
    "",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
)
def get_users(
    role: UserRole | None = None,
    _: Annotated[
        User,
        Depends(
            requires_role(
                UserRole.ADMIN
            )
        ),
    ] = None,
    db: Annotated[
        Session,
        Depends(get_db),
    ] = None,
):

    return UserService.get_all_users(
        db=db,
        role=role,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def get_user(
    user_id: int,
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

    return UserService.get_user_by_id(
        db=db,
        user_id=user_id,
    )


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def update_user(
    user_id: int,
    data: UserUpdate,
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

    user = UserService.get_user_by_id(
        db=db,
        user_id=user_id,
    )

    return UserService.update_user(
        db=db,
        user=user,
        data=data,
    )


@router.patch(
    "/{user_id}/status",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def update_user_status(
    user_id: int,
    data: UserStatusUpdate,
    current_user: Annotated[
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

    user = UserService.get_user_by_id(
        db=db,
        user_id=user_id,
    )

    return UserService.update_status(
        db=db,
        user=user,
        status=data.status,
        current_user_id=current_user.user_id,
    )