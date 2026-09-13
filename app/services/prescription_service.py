#from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.exceptions import BusinessException, ConflictException, NotFoundException, ForbiddenException
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus, MedicineStatus, InvoiceStatus
from app.models.medicine import Medicine
from app.models.medical_record import MedicalRecord
from app.models.prescription import Prescription
from app.models.prescription_detail import PrescriptionDetail
#from  app.models.user import Doctor
from app.models.working_schedule import WorkingSchedule
from app.schemas.prescription import PrescriptionCreate, PrescriptionUpdate
from app.services.invoice_service import InvoiceService

class PrescriptionService:
    @staticmethod
    def get_prescription_by_id(
            db: Session,
            prescription_id: int,
    ) -> Prescription:

        stmt = (
            select(Prescription)
            .options(
                joinedload(Prescription.details)
                .joinedload(PrescriptionDetail.medicine)
            )
            .where(Prescription.prescription_id == prescription_id)
        )

        prescription = db.execute(stmt).unique().scalar_one_or_none()

        if prescription is None:
            raise NotFoundException("Khong tim thay don thuoc")

        return prescription

    @staticmethod
    def get_by_record(
            db: Session,
            record_id: int,
    ) -> Prescription:

        stmt = (
            select(Prescription)
            .options(
                joinedload(Prescription.details)
                .joinedload(PrescriptionDetail.medicine)
            )
            .where(Prescription.record_id == record_id)
        )

        prescription = db.execute(stmt).unique().scalar_one_or_none()

        if prescription is None:
            raise NotFoundException("MedicalRecord chua co don thuoc")

        return prescription

    @staticmethod
    def get_record(
            db: Session,
            record_id: int,
    ) -> MedicalRecord:

        record = db.get(MedicalRecord, record_id)

        if record is None:
            raise NotFoundException("Khong tim thay ho so benh an")

        return record

    @staticmethod
    def get_patient_prescriptions(
            db:Session,
            patient_id: int,
    ) -> list[Prescription]:
        stmt = (
            select(Prescription)
            .join(
                MedicalRecord,
                Prescription.record_id == MedicalRecord.record_id,
            )
            .join(
                Appointment,
                MedicalRecord.appointment_id == Appointment.appointment_id,
            )
            .options(
                selectinload(Prescription.details)
                .selectinload(PrescriptionDetail.medicine),

                selectinload(Prescription.medical_record)
                .selectinload(MedicalRecord.appointment)
            )
            .where(Appointment.patient_id == patient_id)
            .order_by(Prescription.prescription_id.desc())
        )

        return db.execute(stmt).scalars().all()

    @staticmethod
    def check_doctor_ownership(
            db: Session,
            record: MedicalRecord,
            doctor_id: int,
    ) -> None:

        stmt = (
            select(WorkingSchedule)
            .join(
                Appointment,
                Appointment.schedule_id == WorkingSchedule.schedule_id,
            )
            .where(
                Appointment.appointment_id == record.appointment_id,
                WorkingSchedule.doctor_id == doctor_id,
            )
        )

        result = db.execute(stmt).scalar_one_or_none()

        if result is None:
            raise NotFoundException("Bac si khong phu trach ho so nay")

    @staticmethod
    def check_prescription_doctor_ownership(
            db: Session,
            prescription: Prescription,
            doctor_id: int,
    ) -> None:
        record = PrescriptionService.get_record(
            db=db,
            record_id=prescription.record_id,
        )

        PrescriptionService.check_doctor_ownership(
            db=db,
            record=record,
            doctor_id=doctor_id,
        )

    @staticmethod
    def create_prescription(
            db: Session,
            data: PrescriptionCreate,
            doctor_id: int,
    ) -> Prescription:
        record = PrescriptionService.get_record(
            db=db,
            record_id=data.record_id
        )

        PrescriptionService.check_doctor_ownership(
            db=db,
            record=record,
            doctor_id=doctor_id,
        )

        appointment = db.get(Appointment, record.appointment_id)

        if appointment is None:
            raise NotFoundException("Khong tim thay lich hen")

        if appointment.status != AppointmentStatus.CONFIRMED:
            raise BusinessException("Chi co the tao don thuoc khi lich hen dang duoc kham")

        stmt = (
            select(Prescription)
            .where(Prescription.record_id == data.record_id)
        )

        existing_prescription = db.execute(stmt).scalar_one_or_none()

        if existing_prescription is not None:
            raise ConflictException("MedicalRecord da co don thuoc")

        medicine_ids = [
            detail.medicine_id
            for detail in data.details
        ]

        if len(medicine_ids) != len(set(medicine_ids)):
            raise ConflictException("Khong duoc ke cung 1 thuoc nhieu lan trong 1 don")

        medicines = {}

        for medicine_id in medicine_ids:
            medicine = db.get(Medicine, medicine_id)

            if medicine is None:
                raise NotFoundException(f"Khong tim thay thuoc ID={medicine_id}")

            if medicine.status != MedicineStatus.ACTIVE:
                raise BusinessException(f"Thuoc '{medicine.name}' da ngung su dung")

            medicines[medicine_id] = medicine

        for detail in data.details:
            medicine = medicines[detail.medicine_id]

            if detail.quantity > medicine.stock_qty:
                raise BusinessException(f"Thuoc '{medicine.name}' khong du ton kho")

        prescription = Prescription(record_id=data.record_id)

        db.add(prescription)
        db.flush()

        for detail in data.details:
            prescription_detail = PrescriptionDetail(
                prescription_id=prescription.prescription_id,
                medicine_id=detail.medicine_id,
                quantity=detail.quantity,
                dosage=detail.dosage,
                usage_note=detail.usage_note,
            )

            db.add(prescription_detail)

        db.commit()
        db.refresh(prescription)

        return PrescriptionService.get_prescription_by_id(
            db=db,
            prescription_id=prescription.prescription_id,
        )

    @staticmethod
    def update_prescription(
            db: Session,
            prescription: Prescription,
            data: PrescriptionUpdate,
            doctor_id: int,
    ) -> Prescription:

        record = PrescriptionService.get_record(
            db=db,
            record_id=prescription.record_id
        )

        PrescriptionService.check_doctor_ownership(
            db=db,
            record=record,
            doctor_id=doctor_id,
        )

        appointment = db.get(Appointment, record.appointment_id)

        if appointment is None:
            raise NotFoundException("Khong tim thay lich hen")

        if appointment.status not in (
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.COMPLETED
        ):
            raise BusinessException("Khong the sua don thuoc o trang thai hien tai")

        invoice = appointment.invoice

        if invoice is not None:
            if invoice.status == InvoiceStatus.PAID:
                raise BusinessException("Khong the sua don thuoc khi hoa don da thanh toan")

        medicine_ids = [
            detail.medicine_id
            for detail in data.details
        ]

        if len(medicine_ids) != len(set(medicine_ids)):
            raise ConflictException("Khong duoc ke cung 1 thuoc nhieu lan trong 1 don")

        medicines: dict[int, Medicine] = {}

        for medicine_id in medicine_ids:
            medicine = db.get(Medicine, medicine_id)

            if medicine is None:
                raise NotFoundException(f"Khong tim thay thuoc ID={medicine_id}")

            if medicine.status != MedicineStatus.ACTIVE:
                raise BusinessException(f"thuoc '{medicine.name}' da ngung su dung")

            medicines[medicine_id] = medicine

        for detail in data.details:

            medicine = medicines[detail.medicine_id]

            if detail.quantity > medicine.stock_qty:
                raise BusinessException(f"Thuoc '{medicine.name}' khong du ton kho")

        prescription.details.clear()

        for detail in data.details:

            prescription.details.append(
                PrescriptionDetail(
                    medicine_id=detail.medicine_id,
                    quantity=detail.quantity,
                    dosage=detail.dosage,
                    usage_note=detail.usage_note,
                )
            )

        db.flush()

        if invoice is not None:
            invoice.total_amount = (
                InvoiceService.calculate_total_amount(
                    db=db,
                    appointment=appointment,
                )
            )

        db.commit()
        db.refresh(prescription)

        return PrescriptionService.get_prescription_by_id(
            db=db,
            prescription_id=prescription.prescription_id,
        )

