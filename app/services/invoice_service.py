from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException, ConflictException, NotFoundException, ForbiddenException
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus, InvoiceStatus, PaymentMethod, UserRole
from app.models.invoice import Invoice
from app.models.medicine import Medicine
from app.models.user import User
from app.schemas.invoice import InvoiceCreate, InvoicePaymentRequest

class InvoiceService:

    CONSULTATION_FEE = Decimal("100000.00")

    @staticmethod
    def get_invoice_by_id(
            db: Session,
            invoice_id: int,
    ) -> Invoice:

        invoice = db.get(Invoice, invoice_id)

        if invoice is None:
            raise NotFoundException("Khong tim thay hoa don")

        return invoice

    @staticmethod
    def get_invoice_by_appointment(
            db: Session,
            appointment_id: int,
    ) -> Invoice:

        stmt = (
            select(Invoice)
            .where(Invoice.appointment_id == appointment_id)
        )

        invoice = db.execute(stmt).scalar_one_or_none()

        if invoice is None:
            raise NotFoundException("lich hen chua co hoa don")

        return invoice

    @staticmethod
    def get_appointment(
            db: Session,
            appointment_id: int,
    ) -> Appointment:

        appointment = db.get(Appointment, appointment_id)

        if appointment is None:
            raise NotFoundException("Khong tim thay lich hen")

        return appointment

    @staticmethod
    def calculate_medicine_total(
            db: Session,
            appointment: Appointment,
    ) -> Decimal:

        record = appointment.medical_record

        if record is None:
            return Decimal("0.00")

        prescription = record.prescription

        if prescription is None:
            return Decimal("0.00")

        total = Decimal("0.00")

        for detail in prescription.details:
            medicine =  db.get(Medicine, detail.medicine_id)

            if medicine is None:
                raise NotFoundException(f"Khong tim thay thuoc ID={detail.medicine_id}")

            total += medicine.price * detail.quantity

        return total

    @staticmethod
    def calculate_total_amount(
            db: Session,
            appointment: Appointment,
    ) -> Decimal:

        medicine_total = InvoiceService.calculate_medicine_total(
            db=db,
            appointment=appointment,
        )

        return InvoiceService.CONSULTATION_FEE + medicine_total

    @staticmethod
    def create_invoice(
            db: Session,
            data: InvoiceCreate,
    ) -> Invoice:

        appointment = InvoiceService.get_appointment(
            db=db,
            appointment_id=data.appointment_id,
        )

        if appointment.status != AppointmentStatus.COMPLETED:
            raise BusinessException("Chi co the tao hoa don khi lich hen da hoan thanh")

        stmt = (
            select(Invoice)
            .where(Invoice.appointment_id == appointment.appointment_id)
        )

        existing_invoice = db.execute(stmt).scalar_one_or_none()

        if existing_invoice is not None:
            raise ConflictException("Lich hen da co hoa don")

        total_amount = InvoiceService.calculate_total_amount(
            db=db,
            appointment=appointment,
        )

        invoice = Invoice(
            appointment_id=appointment.appointment_id,
            total_amount=total_amount,
            status=InvoiceStatus.UNPAID,
            payment_method=None,
            paid_at=None,
        )

        db.add(invoice)
        db.commit()
        db.refresh(invoice)

        return invoice

    @staticmethod
    def validate_patient_access(
            invoice: Invoice,
            current_user: User,
    ) -> None:
        if current_user.role != UserRole.PATIENT:
            return

        if invoice.appointment.patient_id != current_user.user_id:
            raise ForbiddenException("Ban chi duoc xem hoa don cua chinh minh")

    @staticmethod
    def recalculate_invoice_total(
            db: Session,
            invoice: Invoice,
    ) -> Invoice:
        if invoice.status == InvoiceStatus.PAID:
            raise BusinessException("Khong the cap nha tong tien hoa don da thanh toan")

        appointment = InvoiceService.get_appointment(
            db=db,
            appointment_id=invoice.appointment_id,
        )

        invoice.total_amount = (
            InvoiceService.calculate_total_amount(
                db=db,
                appointment=appointment,
            )
        )

        return invoice

    @staticmethod
    def pay_invoice(
            db: Session,
            invoice: Invoice,
            data: InvoicePaymentRequest,
            current_user: User
    ) -> Invoice:

        if invoice.status == InvoiceStatus.PAID:
            raise ConflictException("Hoa don da duoc thanh toan")

        appointment = InvoiceService.get_appointment(
            db=db,
            appointment_id=invoice.appointment_id,
        )

        if current_user.role == UserRole.PATIENT:
            if appointment.patient_id != current_user.user_id:
                raise ForbiddenException("Ban chi duoc thanh toan hoa don cua chinh minh")

            if data.payment_method != PaymentMethod.ONLINE:
                raise BusinessException("Benh nhan chi duoc thanh toan Online")

        elif current_user.role == UserRole.DOCTOR:
            raise ForbiddenException("Bac si khong co quyen thanh toan hoa don")

        if appointment.status != AppointmentStatus.COMPLETED:
            raise BusinessException("Lich hen chua hoan tat")

        record = appointment.medical_record

        if record is not None:
            prescription = record.prescription

            if prescription is not None:
                for detail in prescription.details:
                    medicine = db.get(Medicine, detail.medicine_id)

                    if medicine is None:
                        raise NotFoundException(f"Khong tim thay thuoc ID={detail.medicine_id}")

                    if detail.quantity > medicine.stock_qty:
                        raise BusinessException(f"Thuoc '{medicine.name}' khong du ton kho de thanh toan")

                    medicine.stock_qty -= detail.quantity

        invoice.status = InvoiceStatus.PAID

        invoice.payment_method = data.payment_method

        invoice.paid_at = datetime.now()

        db.commit()
        db.refresh(invoice)

        return invoice

