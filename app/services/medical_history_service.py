from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus
from app.models.working_schedule import WorkingSchedule
from app.models.prescription_detail import PrescriptionDetail
from app.models.medical_record import MedicalRecord
from app.models.prescription import Prescription
from app.core.exceptions import NotFoundException, ForbiddenException, BusinessException
from app.models.user import Doctor


class MedicalHistoryService:

    @staticmethod
    def get_my_medical_history(
            db: Session,
            patient_id: int
    ):
        stmt = (
            select(Appointment)
            .options(
                joinedload(Appointment.schedule)
                .joinedload(WorkingSchedule.doctor)
                .joinedload(Doctor.specialty),

                joinedload(Appointment.medical_record)
                .joinedload(MedicalRecord.prescription)
                .joinedload(Prescription.details)
                .joinedload(PrescriptionDetail.medicine)
            )
            .where(
                Appointment.patient_id == patient_id,
                Appointment.status == AppointmentStatus.COMPLETED
            )
            .order_by(Appointment.appointment_time.desc())
        )

        appointments = db.execute(stmt).unique().scalars().all()

        return MedicalHistoryService._build_history_response(appointments)

    @staticmethod
    def get_previous_medical_history_for_doctor(
            db: Session,
            appointment_id: int,
            doctor_id: int
    ):
        current_appointment = db.get(
            Appointment,
            appointment_id
        )

        if current_appointment is None:
            raise NotFoundException("Khong tim thay lich hen")

        stmt_ownership = (
            select(WorkingSchedule)
            .where(
                WorkingSchedule.schedule_id == current_appointment.schedule_id,

                WorkingSchedule.doctor_id == doctor_id,
            )
        )

        schedule = db.execute(stmt_ownership).scalar_one_or_none()

        if schedule is None:
            raise ForbiddenException("Bac si khong phu trach lich hen nay")

        if current_appointment.status == AppointmentStatus.CANCELLED:
            raise BusinessException("Khong the xem lich su tu lich hen da huy")

        patient_id = current_appointment.patient_id

        stmt = (
            select(Appointment)
            .join(
                MedicalRecord,
                MedicalRecord.appointment_id == Appointment.appointment_id
            )
            .options(
                joinedload(Appointment.schedule)
                .joinedload(WorkingSchedule.doctor)
                .joinedload(Doctor.specialty),

                joinedload(Appointment.medical_record)
                .joinedload(MedicalRecord.prescription)
                .joinedload(Prescription.details)
                .joinedload(PrescriptionDetail.medicine)
            )
            .where(
                Appointment.patient_id == patient_id,

                Appointment.status == AppointmentStatus.COMPLETED,

                Appointment.appointment_id != current_appointment.appointment_id,

                Appointment.appointment_time < current_appointment.appointment_time,
            )
            .order_by(Appointment.appointment_time.desc())
        )

        appointments = db.execute(stmt).unique().scalars().all()

        return MedicalHistoryService._build_history_response(appointments)

    @staticmethod
    def _build_history_response(
            appointments: list[Appointment]
    ):
        items = []

        for appointment in appointments:
            schedule = appointment.schedule

            doctor = schedule.doctor

            record = appointment.medical_record

            prescription = (
                record.prescription
                if record is not None
                else None
            )

            prescription_response = None

            if prescription is not None:
                medicines = []

                for detail in prescription.details:
                    medicine = detail.medicine

                    medicines.append({
                        "medicine_id": medicine.medicine_id,
                        "name": medicine.name,
                        "unit": medicine.unit,
                        "price": medicine.price,
                        "quantity": detail.quantity,
                        "dosage": detail.dosage,
                        "usage_note": detail.usage_note,
                    })

                prescription_response = {
                    "prescription_id": prescription.prescription_id,

                    "created_at": prescription.created_at,

                    "medicines": medicines,
                }

            items.append({
                "appointment_id": appointment.appointment_id,

                "appointment_time": appointment.appointment_time,

                "doctor_id": doctor.user_id,

                "doctor_name": doctor.full_name,

                "specialty_id": (
                    doctor.specialty_id
                    if doctor is not None
                    else None
                ),

                "specialty_name": (
                    doctor.specialty.name
                    if doctor.specialty is not None
                    else None
                ),

                "examined_at": (
                    record.examined_at
                    if record is not None
                    else None
                ),

                "symptoms": (
                    record.symptoms
                    if record is not None
                    else None
                ),

                "diagnosis": (
                    record.diagnosis
                    if record is not None
                    else None
                ),

                "note": (
                    record.note
                    if record is not None
                    else None
                ),

                "prescription": prescription_response,
            })

        return {
            "items": items,
        }

