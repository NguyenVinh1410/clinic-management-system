from typing import Annotated

from fastapi import Depends, APIRouter, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, requires_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.doctor import DoctorUpdate, DoctorResponse
from app.services.doctor_service import DoctorService

router = APIRouter(
    prefix="/api/doctor",
    tags=["doctor"],
)

@router.get(
    "",
    response_model=list[DoctorResponse],
    status_code=status.HTTP_200_OK,
)
def get_doctors(
        _: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.DOCTOR,
                UserRole.RECEPTIONIST,
                UserRole.PATIENT
            ))
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ]
):

    return DoctorService.get_all_doctors(db=db)

@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse,
    status_code=status.HTTP_200_OK,
)
def get_doctor(
        doctor_id: int,
        _: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.DOCTOR,
                UserRole.RECEPTIONIST,
                UserRole.PATIENT
            ))
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ]
):

    return DoctorService.get_doctor_by_id(db=db, doctor_id=doctor_id)

@router.patch(
    "/{doctor_id}",
    response_model=DoctorResponse,
    status_code=status.HTTP_200_OK,
)
def update_doctor(
        doctor_id: int,
        data: DoctorUpdate,
        _: Annotated[
            User,
            Depends(requires_role(UserRole.ADMIN))
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ]
):

    doctor = DoctorService.get_doctor_by_id(db=db, doctor_id=doctor_id)

    return DoctorService.update_doctor(
        db=db,
        doctor=doctor,
        data=data,
    )

@router.delete(
    "/{doctor_id}",
    response_model=DoctorResponse,
    status_code=status.HTTP_200_OK,
)
def deactivate_doctor(
        doctor_id: int,
        _: Annotated[
            User,
            Depends(requires_role(UserRole.ADMIN))
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ]
):

    doctor = DoctorService.get_doctor_by_id(db=db, doctor_id=doctor_id)

    return DoctorService.deactivate_doctor(db=db, doctor=doctor)