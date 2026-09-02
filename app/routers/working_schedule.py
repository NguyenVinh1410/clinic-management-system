from typing import Annotated

from fastapi import Depends, APIRouter, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, requires_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.working_schedule import WorkingScheduleCreate, WorkingScheduleResponse, WorkingScheduleUpdate
from app.services.working_schedule_service import WorkingScheduleService

router = APIRouter(
    prefix="/api/working_schedule",
    tags=["Working Schedule"],
)

@router.post(
    "",
    response_model=WorkingScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_schedule(
    data: WorkingScheduleCreate,
    _: Annotated[
        User,
        Depends(requires_role(UserRole.ADMIN)),
    ],
    db: Annotated[Session, Depends(get_db)],
):
    return WorkingScheduleService.create_schedule(
        db=db,
        data=data,
    )

@router.get(
    "",
    response_model=list[WorkingScheduleResponse],
    status_code=status.HTTP_200_OK,
)
def get_schedule(
        _: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.DOCTOR,
                UserRole.PATIENT,
                UserRole.RECEPTIONIST,
            ))
        ],
        db: Annotated[Session, Depends(get_db)],
):
    return WorkingScheduleService.get_all_schedules(db=db)

@router.get(
    "/doctor/{doctor_id}",
    response_model=list[WorkingScheduleResponse],
    status_code=status.HTTP_200_OK,
)
def get_doctor_schedule(
        doctor_id: int,
        _: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.DOCTOR,
                UserRole.PATIENT,
                UserRole.RECEPTIONIST,
            ))
        ],
        db: Annotated[Session, Depends(get_db)],
):
    return (WorkingScheduleService.get_schedule_by_doctor(
        db=db,
        doctor_id=doctor_id,
    ))

@router.get(
    "/{schedule_id}",
    response_model=WorkingScheduleResponse,
    status_code=status.HTTP_200_OK,
)
def get_schedule(
        schedule_id: int,
        _: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.DOCTOR,
                UserRole.PATIENT,
                UserRole.RECEPTIONIST,
            ))
        ],
        db: Annotated[Session, Depends(get_db)],
):
    return WorkingScheduleService.get_schedule_by_id(
        db=db,
        schedule_id=schedule_id,
    )

@router.patch(
    "/{schedule_id}",
    response_model=WorkingScheduleResponse,
    status_code=status.HTTP_200_OK,
)
def update_schedule(
        schedule_id: int,
        data: WorkingScheduleUpdate,
        _: Annotated[
            User,
            Depends(requires_role(UserRole.ADMIN))
        ],
        db: Annotated[Session, Depends(get_db)],
):
    schedule = (
        WorkingScheduleService.get_schedule_by_id(
            db=db,
            schedule_id=schedule_id,
        )
    )

    return WorkingScheduleService.update_schedule(
        db=db,
        schedule=schedule,
        data=data,
    )

@router.delete(
    "/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_schedule(
        schedule_id: int,
        _: Annotated[
            User,
            Depends(requires_role(UserRole.ADMIN))
        ],
        db: Annotated[Session, Depends(get_db)],
):
    schedule = (
        WorkingScheduleService.get_schedule_by_id(
            db=db,
            schedule_id=schedule_id,
        )
    )

    WorkingScheduleService.delete_schedule(
        db=db,
        schedule=schedule,
    )

    return None