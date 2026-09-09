from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, requires_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"],
)

@router.get(
    "",
    response_model=DashboardResponse,
)
def get_dashboard(
        _: Annotated[
            User,
            Depends(requires_role(UserRole.ADMIN)),
        ],
        db: Annotated[
            Session,
            Depends(get_db)
        ],
):
    return DashboardService.get_dashboard(db=db)