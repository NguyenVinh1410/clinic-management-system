from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, requires_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.patient import PatientResponse, PatientUpdate
from app.services.patient_service import PatientService

router = APIRouter(
    prefix="/api/patient",
    tags=["Patients"],
)


# @router.post(
#     "",
#     response_model=PatientResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# def create_patient(
#         data: PatientCreate,
#         _: Annotated[
#             User,
#             Depends(requires_role(
#                 UserRole.ADMIN,
#                 UserRole.RECEPTIONIST)),
#         ],
#         db: Annotated[
#             Session,
#             Depends(get_db),
#         ],
# ):
#     return PatientService.create_patient(
#         db=db,
#         data=data,
#     )


@router.get(
    "/me",
    response_model=PatientResponse,
    status_code=status.HTTP_200_OK,
)
def get_my_profile(
    current_user: Annotated[
        User,
        Depends(requires_role(UserRole.PATIENT)),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    return PatientService.get_patient_by_id(
        db=db,
        patient_id=current_user.user_id,
    )


@router.patch(
    "/me",
    response_model=PatientResponse,
    status_code=status.HTTP_200_OK,
)
def update_my_profile(
    data: PatientUpdate,
    current_user: Annotated[
        User,
        Depends(requires_role(UserRole.PATIENT)),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    patient = PatientService.get_patient_by_id(
        db=db,
        patient_id=current_user.user_id,
    )

    update_data = data.model_dump(exclude_unset=True)

    return PatientService.update_patient(
        db=db,
        patient=patient,
        data=update_data,
    )


@router.get(
    "",
    response_model=list[PatientResponse],
    status_code=status.HTTP_200_OK,
)
def get_patients(
        _: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.RECEPTIONIST)),
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ],
):
    return PatientService.get_all_patients(db=db)

@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    status_code=status.HTTP_200_OK,
)
def get_patient(
        patient_id: int,
        _: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.RECEPTIONIST)),
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ],
):
    return PatientService.get_patient_by_id(
        db=db,
        patient_id=patient_id,
    )