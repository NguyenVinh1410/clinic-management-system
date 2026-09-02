from typing import Annotated

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas.auth import TokenResponse, UserResponse, RegisterRequest
from app.models.user import User
from app.services.auth_service import AuthService
from app.schemas.patient import PatientResponse

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)

@router.post(
    "/register",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)

def register(
        data: RegisterRequest,
        db: Annotated[
            Session,
            Depends(get_db),
        ],
):
    return AuthService.register_patient(
        db=db,
        data=data,
    )

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)

def login(
    data: Annotated[OAuth2PasswordRequestForm, Depends()], #LoginRequest
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):

    access_token = AuthService.login(
        db=db,
        username=data.username,
        password=data.password,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)

def get_me(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    return current_user