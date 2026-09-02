from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session, deferred

from app.dependencies import get_db, requires_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.specialty import SpecialtyCreate, SpecialtyUpdate, SpecialtyResponse
from app.services.specialty_service import SpecialtyService

router = APIRouter(
    prefix="/api/specialty",
    tags=["specialty"],
)

@router.post(
    "",
    response_model=SpecialtyResponse,
    status_code=status.HTTP_201_CREATED,
)

def create_specialty(
        data: SpecialtyCreate,
        _: Annotated[
            User,
            Depends(requires_role(UserRole.ADMIN)),
        ],
        db: Annotated[Session, Depends(get_db)],
):

    return SpecialtyService.create_specialty(
        db=db,
        name=data.name,
        description=data.description,
    )

@router.get(
    "",
    response_model=list[SpecialtyResponse],
)

def get_specialties(
        _: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.RECEPTIONIST,
                UserRole.PATIENT,
                UserRole.DOCTOR,
            )),
        ],
        db: Annotated[Session, Depends(get_db)],
):

    return SpecialtyService.get_all_specialties(
        db=db
    )

@router.get(
    "/{specialty_id}",
    response_model=SpecialtyResponse,
)
def get_specialty(
        specialty_id: int,
        _: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.RECEPTIONIST,
                UserRole.PATIENT,
                UserRole.DOCTOR,
            ))
        ],
        db: Annotated[Session, Depends(get_db)],
):

    return SpecialtyService.get_specialty_by_id(
        db=db,
        specialty_id=specialty_id,
    )

@router.patch(
    "/{specialty_id}",
    response_model=SpecialtyResponse,
)
def update_specialty(
        specialty_id: int,
        data: SpecialtyUpdate,
        _: Annotated[
            User,
            Depends(requires_role(UserRole.ADMIN)),
        ],
        db: Annotated[Session, Depends(get_db)],
):

    specialty = (
        SpecialtyService.get_specialty_by_id(
            db=db,
            specialty_id=specialty_id,
        )
    )

    update_data = data.model_dump(exclude_unset=True)

    return SpecialtyService.update_specialty(
        db=db,
        specialty=specialty,
        data=update_data,
    )

@router.delete(
    "/{specialty_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_specialty(
        specialty_id: int,
        _: Annotated[
            User,
            Depends(requires_role(UserRole.ADMIN)),
        ],
        db: Annotated[Session, Depends(get_db)],
):

    SpecialtyService.delete_specialty(
        db=db,
        specialty_id=specialty_id,
    )

    return None