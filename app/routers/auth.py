from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)

def login(
        data: LoginRequest,
        db: Annotated[
            Session,
            Depends(get_db),
        ]
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