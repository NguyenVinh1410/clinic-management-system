from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user, requires_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordResponse, MedicalRecordUpdate
from app.services.medical_record_service import MedicalRecordService

router = APIRouter(
    prefix="/api/medical_record",
    tags=["medical record"],
)

@router.post(
    "",
    response_model=MedicalRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_medical_record(
        data: MedicalRecordCreate,
        current_user: Annotated[
            User,
            Depends(requires_role(UserRole.DOCTOR))
        ],

        db: Annotated[
            Session,
            Depends(get_db),
        ]
):
    return MedicalRecordService.create_record(
        db=db,
        data=data,
        doctor_id=current_user.user_id
    )

@router.get(
    "",
    response_model=list[MedicalRecordResponse],
)
def get_medical_records(
        _: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.RECEPTIONIST,
                UserRole.DOCTOR
            ))
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ]
):
    return MedicalRecordService.get_all_records(db=db)

@router.get(
    "/appointment/{appointment_id}",
    response_model=MedicalRecordResponse,
)
def get_record_by_appointment(
        appointment_id: int,
        current_user: Annotated[
            User,
            Depends(get_current_user)
        ],

        db: Annotated[
            Session,
            Depends(get_db),
        ]
):
    record = MedicalRecordService.get_record_by_appointment(
        db=db,
        appointment_id=appointment_id
    )

    if current_user.role == UserRole.DOCTOR:
        MedicalRecordService.check_doctor_ownership(
            db=db,
            appointment=MedicalRecordService.get_appointment(
                db=db,
                appointment_id=appointment_id
            ),
            doctor_id=current_user.user_id
        )

    elif current_user.role not in (
        UserRole.ADMIN,
        UserRole.RECEPTIONIST,
    ):
        from app.core.exceptions import ForbiddenException

        raise ForbiddenException("Ban khong co quyen xem ho so benh an")

    return record

@router.get(
    "/{record_id}",
    response_model=MedicalRecordResponse,
)
def get_medical_record(
        record_id: int,
        current_user: Annotated[
            User,
            Depends(get_current_user)
        ],

        db: Annotated[
            Session,
            Depends(get_db),
        ]
):
    record = MedicalRecordService.get_record_by_id(db=db, record_id=record_id)

    if current_user.role == UserRole.DOCTOR:
        appointment = MedicalRecordService.get_appointment(
            db=db,
            appointment_id=record.appointment_id
        )

        MedicalRecordService.check_doctor_ownership(
            db=db,
            appointment=appointment,
            doctor_id=current_user.user_id
        )

    elif current_user.role not in (
        UserRole.ADMIN,
        UserRole.RECEPTIONIST,
    ):
        from app.core.exceptions import ForbiddenException

        raise ForbiddenException("Ban khong co quyen xem ho so benh an")

    return record

@router.patch(
    "/{record_id}",
    response_model=MedicalRecordResponse,
)
def update_medical_record(
        record_id: int,
        data: MedicalRecordUpdate,
        current_user: Annotated[
            User,
            Depends(requires_role(UserRole.DOCTOR))
        ],

        db: Annotated[
            Session,
            Depends(get_db),
        ]
):
    record = MedicalRecordService.get_record_by_id(db=db, record_id=record_id)

    return MedicalRecordService.update_record(
        db=db,
        record=record,
        data=data,
        doctor_id=current_user.user_id
    )