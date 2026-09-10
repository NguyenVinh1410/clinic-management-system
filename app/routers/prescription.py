from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, requires_role
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
    "/record/{record_id}",
    response_model=PrescriptionResponse,
)
def get_prescription_by_record(
        record_id: int,
        _: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.DOCTOR,
                UserRole.RECEPTIONIST
            ))
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ]
):
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
        _: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.DOCTOR,
                UserRole.RECEPTIONIST
            ))
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ]
):
    return PrescriptionService.get_prescription_by_id(
        db=db,
        prescription_id=prescription_id,
    )


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
