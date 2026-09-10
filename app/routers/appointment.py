from typing import Annotated

from fastapi import Depends, APIRouter, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db, requires_role
from app.models.enums import AppointmentStatus, UserRole
from app.models.user import User
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse, AppointmentStatusUpdate
from app.services.appointment_service import AppointmentService

router = APIRouter(
    prefix="/api/appointment",
    tags=["appointment"],
)


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_appointment(
        data: AppointmentCreate,
        current_user: Annotated[
            User,
            Depends(get_current_user),
        ],
        db: Annotated[Session, Depends(get_db)],
):
    return AppointmentService.create_appointment(
        db=db,
        data=data,
        current_user=current_user,
    )


@router.get(
    "",
    response_model=list[AppointmentResponse],
)
def get_all_appointments(
        _: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.RECEPTIONIST
            )),
        ],
        db: Annotated[Session, Depends(get_db)],
):
    return AppointmentService.get_all_appointments(db=db)


@router.get(
    "/my",
    response_model=list[AppointmentResponse],
)
def get_my_appointments(
        current_user: Annotated[
            User,
            Depends(requires_role(UserRole.PATIENT))
        ],
        db: Annotated[Session, Depends(get_db)],
):
    return AppointmentService.get_appointments_by_patient(
        db=db,
        patient_id=current_user.user_id
    )


@router.get(
    "/patient/{patient_id}",
    response_model=list[AppointmentResponse],
)
def get_patient_appointments(
        patient_id: int,
        _: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.RECEPTIONIST
            ))
        ],
        db: Annotated[Session, Depends(get_db)],
):
    return AppointmentService.get_appointments_by_patient(
        db=db,
        patient_id=patient_id,
    )


@router.get(
    "/doctor/{doctor_id}",
    response_model=list[AppointmentResponse],
)
def get_doctor_appointments(
        doctor_id: int,
        current_user: Annotated[
            User,
            Depends(get_current_user),
        ],
        db: Annotated[Session, Depends(get_db)],
):
    if current_user.role == UserRole.DOCTOR:
        if current_user.user_id != doctor_id:
            from app.core.exceptions import ForbiddenException

            raise ForbiddenException("Bac si chi duoc xem lich cua chinh minh")

    elif current_user.role not in (
            UserRole.ADMIN,
            UserRole.RECEPTIONIST,
    ):
        from app.core.exceptions import ForbiddenException

        raise ForbiddenException("Ban khong co quyen xem lich cua bac si")

    return AppointmentService.get_appointments_by_doctor(
        db=db,
        doctor_id=doctor_id,
    )


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
def get_appointment(
        appointment_id: int,
        current_user: Annotated[
            User,
            Depends(get_current_user),
        ],
        db: Annotated[Session, Depends(get_db)],
):
    appointment = (
        AppointmentService.get_appointment_by_id(
            db=db,
            appointment_id=appointment_id,
        )
    )

    if current_user.role == UserRole.PATIENT:

        if appointment.patient_id != current_user.user_id:
            from app.core.exceptions import ForbiddenException

            raise ForbiddenException("Ban chi duoc xem lich hen cua chinh minh")

    elif current_user.role == UserRole.DOCTOR:
        if not AppointmentService.belong_to_doctor(
            db=db,
            appointment=appointment,
            doctor_id=current_user.user_id
        ):
            from app.core.exceptions import ForbiddenException
            raise ForbiddenException("Bac si chi duoc xem lich hen cua minh")

    return appointment


@router.patch(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
def update_appointment(
        appointment_id: int,
        data: AppointmentUpdate,
        _: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.RECEPTIONIST
            )),
        ],
        db: Annotated[Session, Depends(get_db)],
):
    appointment = (
        AppointmentService.get_appointment_by_id(
            db=db,
            appointment_id=appointment_id,
        )
    )

    return AppointmentService.update_appointment(
        db=db,
        appointment=appointment,
        data=data,
    )


@router.patch(
    "/{appointment_id}/status",
    response_model=AppointmentResponse,
)
def update_appointment_status(
        appointment_id: int,
        data: AppointmentStatusUpdate,
        current_user: Annotated[
            User,
            Depends(get_current_user),
        ],
        db: Annotated[Session, Depends(get_db)],
):
    appointment = AppointmentService.get_appointment_by_id(
        db=db,
        appointment_id=appointment_id,
    )

    if current_user.role in (UserRole.ADMIN, UserRole.RECEPTIONIST):
        return AppointmentService.update_status(
            db=db,
            appointment=appointment,
            new_status=data.status,
        )

    if current_user.role == UserRole.DOCTOR:
        if data.status != AppointmentStatus.COMPLETED:
            from app.core.exceptions import ForbiddenException

            raise ForbiddenException("Bac si chi duoc chuyen lich sang Completed")

        if not AppointmentService.belong_to_doctor(
                db=db,
                appointment=appointment,
                doctor_id=current_user.user_id,
        ):
            from app.core.exceptions import ForbiddenException

            raise ForbiddenException("Lich hen khong thuoc bac si hien tai")

        return AppointmentService.update_status(
            db=db,
            appointment=appointment,
            new_status=data.status,
        )

    from app.core.exceptions import ForbiddenException
    raise ForbiddenException("Ban khong co quyen thay doi trang thai lich hen")


@router.post(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponse,
)
def cancel_appointment(
        appointment_id: int,
        current_user: Annotated[
            User,
            Depends(get_current_user),
        ],
        db: Annotated[Session, Depends(get_db)],
):
    appointment = AppointmentService.get_appointment_by_id(
        db=db,
        appointment_id=appointment_id,
    )

    if current_user.role == UserRole.PATIENT:
        if appointment.patient_id != current_user.user_id:
            from app.core.exceptions import ForbiddenException

            raise ForbiddenException("Ban chi duoc huy lich cua chinh minh")

    elif current_user.role not in (
            UserRole.ADMIN,
            UserRole.RECEPTIONIST,
    ):

        from app.core.exceptions import ForbiddenException

        raise ForbiddenException("Ban khong co quyen huy lich")

    return AppointmentService.cancel_appointment(
        db=db,
        appointment=appointment,
    )
