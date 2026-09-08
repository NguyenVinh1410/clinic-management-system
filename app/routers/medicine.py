from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, requires_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.medicine import MedicineUpdate, MedicineCreate, MedicineResponse
from app.services.medicine_service import MedicineService

router = APIRouter(
    prefix="/api/medicine",
    tags=["medicine"],
)

@router.post(
    "",
    response_model=MedicineResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_medicine(
        data: MedicineCreate,
        _: Annotated[
            User,
            Depends(requires_role(UserRole.ADMIN)),
        ],

        db: Annotated[
            Session,
            Depends(get_db),
        ]
):
    return MedicineService.create_medicine(
        db=db,
        data=data,
    )

@router.get(
    "",
    response_model=list[MedicineResponse],
)
def get_medicines(
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

    return MedicineService.get_all_medicines(db=db)

@router.get(
    "/{medicine_id}",
    response_model=MedicineResponse,
)
def get_medicine(
        medicine_id: int,
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

    return MedicineService.get_medicine_by_id(
        db=db,
        medicine_id=medicine_id,
    )

@router.patch(
    "/{medicine_id}",
    response_model=MedicineResponse,
)
def update_medicine(
        medicine_id: int,
        data: MedicineUpdate,
        _: Annotated[
            User,
            Depends(requires_role(UserRole.ADMIN)),
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ]
):
    medicine = MedicineService.get_medicine_by_id(
        db=db,
        medicine_id=medicine_id,
    )

    return MedicineService.update_medicine(
        db=db,
        medicine=medicine,
        data=data,
    )

@router.delete(
    "/{medicine_id}",
    response_model=MedicineResponse,
)
def discontinue_medicine(
        medicine_id: int,
        _: Annotated[
            User,
            Depends(requires_role(UserRole.ADMIN)),
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ]
):
    medicine = MedicineService.get_medicine_by_id(
        db=db,
        medicine_id=medicine_id,
    )

    return MedicineService.discontinue_medicine(
        db=db,
        medicine=medicine,
    )
