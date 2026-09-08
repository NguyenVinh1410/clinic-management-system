from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, requires_role
from app.models.enums import UserRole
from app.models.user import User
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
    "/{invoice_id}",
    response_model=InvoiceResponse,
)
def get_invoice(
        invoice_id: int,
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
    return InvoiceService.get_invoice_by_id(
        db=db,
        invoice_id=invoice_id,
    )

@router.get(
    "/appointment/{appointment_id}",
    response_model=InvoiceResponse,
)
def get_invoice_by_appointment(
        appointment_id: int,
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
    return InvoiceService.get_invoice_by_appointment(
        db=db,
        appointment_id=appointment_id,
    )

@router.patch(
    "/{invoice_id}/pay",
    response_model=InvoiceResponse,
)
def pay_invoice(
        invoice_id: int,
        data: InvoicePaymentRequest,
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
    invoice = InvoiceService.get_invoice_by_id(
        db=db,
        invoice_id=invoice_id,
    )

    return InvoiceService.pay_invoice(
        db=db,
        invoice=invoice,
        data=data,
    )