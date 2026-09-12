from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.dependencies import get_db, requires_role
from app.models import Appointment
from app.models.enums import UserRole
from app.models.user import User
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceCreate, InvoicePaymentRequest, InvoiceResponse
from app.services.invoice_service import InvoiceService

router = APIRouter(
    prefix="/api/invoice",
    tags=["invoice"],
)

@router.post(
    "",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice(
        data: InvoiceCreate,
        _: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.RECEPTIONIST
            ))
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ]
):
    return InvoiceService.create_invoice(
        db=db,
        data=data,
    )

@router.get(
    "",
    response_model=list[InvoiceResponse],
    status_code=status.HTTP_200_OK,
)
def get_invoices(
        _: Annotated[
            User,
            Depends(
                requires_role(
                    UserRole.ADMIN,
                    UserRole.RECEPTIONIST,
                ))
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ],
):
    return InvoiceService.get_all_invoices(db=db)

@router.get(
    "/my",
    response_model=list[InvoiceResponse],
    status_code=status.HTTP_200_OK,
)
def get_my_invoices(
        current_user: Annotated[
            User,
            Depends(requires_role(UserRole.PATIENT))
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ]
):

    return InvoiceService.get_patient_invoices(
        db=db,
        patient_id=current_user.user_id
    )

@router.get(
    "/{invoice_id}",
    response_model=InvoiceResponse,
    status_code=status.HTTP_200_OK,
)
def get_invoice(
        invoice_id: int,
        current_user: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.RECEPTIONIST,
                UserRole.PATIENT
            ))
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ]
):
    invoice = InvoiceService.get_invoice_by_id(
        db=db,
        invoice_id=invoice_id,
    )

    InvoiceService.validate_patient_access(
        invoice=invoice,
        current_user=current_user,
    )

    return invoice

@router.get(
    "/appointment/{appointment_id}",
    response_model=InvoiceResponse,
    status_code=status.HTTP_200_OK,
)
def get_invoice_by_appointment(
        appointment_id: int,
        current_user: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.RECEPTIONIST,
                UserRole.PATIENT
            ))
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ]
):

    invoice = InvoiceService.get_invoice_by_appointment(
        db=db,
        appointment_id=appointment_id,
    )

    InvoiceService.validate_patient_access(
        invoice=invoice,
        current_user=current_user,
    )

    return invoice

@router.patch(
    "/{invoice_id}/pay",
    response_model=InvoiceResponse,
    status_code=status.HTTP_200_OK,
)
def pay_invoice(
        invoice_id: int,
        data: InvoicePaymentRequest,
        current_user: Annotated[
            User,
            Depends(requires_role(
                UserRole.ADMIN,
                UserRole.RECEPTIONIST,
                UserRole.PATIENT
            ))
        ],
        db: Annotated[
            Session,
            Depends(get_db),
        ]
):
    invoice = InvoiceService.get_invoice_by_id(
        db=db,
        invoice_id=invoice_id,
    )

    return InvoiceService.pay_invoice(
        db=db,
        invoice=invoice,
        data=data,
        current_user=current_user,
    )