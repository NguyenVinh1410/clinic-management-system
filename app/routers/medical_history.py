from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, requires_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.medical_history import MedicalHistoryResponse
from app.services.medical_history_service import MedicalHistoryService

router = APIRouter(
    prefix="/api/patients/me",
    tags=["medical history"],
)

@router.get(
    "/medical_history",
    response_model=MedicalHistoryResponse,
)
def get_my_medical_history(
    current_user: Annotated[
        User,
        Depends(requires_role(UserRole.PATIENT))
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ]
):
    return MedicalHistoryService.get_my_medical_history(
        db=db,
        patient_id=current_user.user_id
    )

doctor_router = APIRouter(
    prefix="/api/medical_history",
    tags=["medical history"],
)
@doctor_router.get(
    "/appointment/{appointment_id}/previous",
    response_model=MedicalHistoryResponse,
)
def get_previous_medical_history_for_doctor(
        appointment_id: int,

        current_user: Annotated[
            User,
            Depends(requires_role(UserRole.DOCTOR))
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ]
):
    return MedicalHistoryService.get_previous_medical_history_for_doctor(
        db=db,
        appointment_id=appointment_id,
        doctor_id=current_user.user_id
    )