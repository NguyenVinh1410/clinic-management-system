from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import BusinessException, ConflictException, NotFoundException, ForbiddenException
from app.models import WorkingSchedule
from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord
from app.models.prescription import Prescription
from app.models.prescription_detail import PrescriptionDetail
from app.models.enums import AppointmentStatus, InvoiceStatus, PaymentMethod, UserRole
from app.models.invoice import Invoice
from app.models.medicine import Medicine
from app.models.user import User, Doctor
from app.schemas.invoice import InvoiceCreate, InvoicePaymentRequest, InvoiceResponse, InvoicePatientInfo, InvoiceDoctorInfo, InvoiceSpecialtyInfo, InvoiceMedicineItem

class InvoiceService:

    CONSULTATION_FEE = Decimal("100000.00")

    @staticmethod
    def get_invoice_by_id(
            db: Session,
            invoice_id: int,
    ) -> Invoice:

        stmt = (
            select(Invoice)
            .options(
                selectinload(Invoice.appointment)
                .selectinload(Appointment.patient),

                selectinload(Invoice.appointment)
                .selectinload(Appointment.schedule)
                .selectinload(WorkingSchedule.doctor)
                .selectinload(Doctor.specialty),

                selectinload(Invoice.appointment)
                .selectinload(Appointment.medical_record)
                .selectinload(MedicalRecord.prescription)
                .selectinload(Prescription.details)
                .selectinload(PrescriptionDetail.medicine)
            )
            .where(Invoice.invoice_id == invoice_id)
        )

        invoice = db.execute(stmt).scalar_one_or_none()

        if invoice is None:
            raise NotFoundException("Khong tim thay hoa don")

        return invoice

    @staticmethod
    def get_all_invoices(db: Session) -> list[InvoiceResponse]:

        stmt = (
            select(Invoice)
            .options(
                selectinload(Invoice.appointment)
                .selectinload(Appointment.patient),

                selectinload(Invoice.appointment)
                .selectinload(Appointment.schedule)
                .selectinload(WorkingSchedule.doctor)
                .selectinload(Doctor.specialty),

                selectinload(Invoice.appointment)
                .selectinload(Appointment.medical_record)
                .selectinload(MedicalRecord.prescription)
                .selectinload(Prescription.details)
                .selectinload(PrescriptionDetail.medicine)
            )
            .order_by(Invoice.invoice_id.desc())
        )

        invoices = db.execute(stmt).scalars().all()

        return [
            InvoiceService.build_invoice_response(invoice)
            for invoice in invoices
        ]

    @staticmethod
    def get_invoice_by_appointment(
            db: Session,
            appointment_id: int,
    ) -> Invoice:

        stmt = (
            select(Invoice)
            .options(
                selectinload(Invoice.appointment)
                .selectinload(Appointment.patient),

                selectinload(Invoice.appointment)
                .selectinload(Appointment.schedule)
                .selectinload(WorkingSchedule.doctor)
                .selectinload(Doctor.specialty),

                selectinload(Invoice.appointment)
                .selectinload(Appointment.medical_record)
                .selectinload(MedicalRecord.prescription)
                .selectinload(Prescription.details)
                .selectinload(PrescriptionDetail.medicine)
            )
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
    def get_patient_invoices(
            db: Session,
            patient_id: int,
    ) -> list[InvoiceResponse]:
        stmt = (
            select(Invoice)
            .join(
                Appointment,
                Invoice.appointment_id == Appointment.appointment_id
            )
            .options(
                selectinload(Invoice.appointment)
                .selectinload(Appointment.patient),

                selectinload(Invoice.appointment)
                .selectinload(Appointment.schedule)
                .selectinload(WorkingSchedule.doctor)
                .selectinload(Doctor.specialty),

                selectinload(Invoice.appointment)
                .selectinload(Appointment.medical_record)
                .selectinload(MedicalRecord.prescription)
                .selectinload(Prescription.details)
                .selectinload(PrescriptionDetail.medicine)
            )
            .where(Appointment.patient_id == patient_id)
            .order_by(Invoice.invoice_id.desc())
        )

        invoices = db.execute(stmt).scalars().all()

        return [
            InvoiceService.build_invoice_response(invoice)
            for invoice in invoices
        ]

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

        if invoice.status == InvoiceStatus.CANCELLED:
            raise BusinessException("Khong the thanh toan hoa don da huy")

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

    @staticmethod
    def build_invoice_response(invoice: Invoice) -> InvoiceResponse:
        appointment = invoice.appointment

        patient = appointment.patient

        doctor = appointment.schedule.doctor

        specialty = doctor.specialty

        medicines = []

        medicine_total = Decimal("0.00")

        record = appointment.medical_record

        if record is not None:
            prescription = record.prescription

            if prescription is not None:
                for detail in prescription.details:
                    medicine = detail.medicine

                    line_total = medicine.price * detail.quantity
                    medicine_total += line_total

                    medicines.append(
                        InvoiceMedicineItem(
                            medicine_id=medicine.medicine_id,
                            medicine_name=medicine.name,
                            unit=medicine.unit,
                            quantity=detail.quantity,
                            unit_price=medicine.price,
                            line_total=line_total,
                            dosage=detail.dosage,
                            usage_note=detail.usage_note,
                        )
                    )

        return InvoiceResponse(
            invoice_id=invoice.invoice_id,
            appointment_id=appointment.appointment_id,
            appointment_time=appointment.appointment_time,

            patient=InvoicePatientInfo(
                patient_id=patient.user_id,
                full_name=patient.full_name,
                phone=patient.phone,
            ),

            doctor=InvoiceDoctorInfo(
                doctor_id=doctor.user_id,
                full_name=doctor.full_name,
            ),

            specialty=InvoiceSpecialtyInfo(
                specialty_id=specialty.specialty_id,
                name=specialty.name,
            ),

            medicines=medicines,

            consultation_fee=InvoiceService.CONSULTATION_FEE,
            medicine_total=medicine_total,
            total_amount=invoice.total_amount,

            status=invoice.status,
            payment_method=invoice.payment_method,
            paid_at=invoice.paid_at,
        )
