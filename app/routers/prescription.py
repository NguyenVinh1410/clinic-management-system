from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException
from app.dependencies import get_db, requires_role, get_current_user
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.prescription import PrescriptionCreate, PrescriptionResponse, PrescriptionUpdate
from app.services.prescription_service import PrescriptionService

router = APIRouter(
    prefix="/api/prescription",
    tags=["prescription"],
)

@router.post(
    "",
    response_model=PrescriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_prescription(
        data: PrescriptionCreate,
        current_user: Annotated[
            User,
            Depends(requires_role(UserRole.DOCTOR))
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ]
):
    return PrescriptionService.create_prescription(
        db=db,
        data=data,
        doctor_id=current_user.user_id
    )

@router.get(
    "/my",
    response_model=list[PrescriptionResponse],
)
def get_my_prescriptions(
        current_user: Annotated[
            User,
            Depends(requires_role(UserRole.PATIENT))
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ]
):
    return PrescriptionService.get_patient_prescriptions(
        db=db,
        patient_id=current_user.user_id,
    )

@router.get(
    "/record/{record_id}",
    response_model=PrescriptionResponse,
)
def get_prescription_by_record(
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
    record = PrescriptionService.get_record(
        db=db,
        record_id=record_id,
    )

    if current_user.role == UserRole.ADMIN:
        pass

    elif current_user.role == UserRole.DOCTOR:
        PrescriptionService.check_doctor_ownership(
            db=db,
            record=record,
            doctor_id=current_user.user_id,
        )

    else:
        raise ForbiddenException("Ban khong co quyen xem don thuoc")

    return PrescriptionService.get_by_record(
        db=db,
        record_id=record_id,
    )

@router.get(
    "/{prescription_id}",
    response_model=PrescriptionResponse,
)
def get_prescription(
        prescription_id: int,

        current_user: Annotated[
            User,
            Depends(get_current_user)
        ],

        db: Annotated[
            Session,
            Depends(get_db),
        ]
):
    prescription = PrescriptionService.get_prescription_by_id(
        db=db,
        prescription_id=prescription_id,
    )

    if current_user.role == UserRole.ADMIN:
        return prescription

    if current_user.role == UserRole.DOCTOR:
        PrescriptionService.check_prescription_doctor_ownership(
            db=db,
            prescription=prescription,
            doctor_id=current_user.user_id,
        )

        return prescription

    raise ForbiddenException("Ban khong co quyen xem don thuoc")

@router.patch(
    "/{prescription_id}",
    response_model=PrescriptionResponse,
    status_code=status.HTTP_200_OK,
)
def update_prescription(
        prescription_id: int,
        data: PrescriptionUpdate,
        current_user: Annotated[
            User,
            Depends(requires_role(UserRole.DOCTOR))
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ]
):
    prescription = PrescriptionService.get_prescription_by_id(
        db=db,
        prescription_id=prescription_id,
    )

    return PrescriptionService.update_prescription(
        db=db,
        prescription=prescription,
        data=data,
        doctor_id=current_user.user_id,
    )
