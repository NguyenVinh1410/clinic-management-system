from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus
from app.models.working_schedule import WorkingSchedule
from app.models.prescription_detail import PrescriptionDetail
from app.models.medical_record import MedicalRecord
from app.models.prescription import Prescription
# from app.core.exceptions import NotFoundException
# from app.models.specialty import Specialty
# from app.models.user import Doctor
# from app.models.medicine import Medicine

class MedicalHistoryService:

    @staticmethod
    def get_my_medical_history(
            db: Session,
            patient_id: int
    ):
        stmt = (
            select(Appointment)
            .options(
                joinedload(Appointment.schedule).joinedload(WorkingSchedule.doctor),
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
                    if hasattr(doctor, "specialty_id")
                    else None
                ),
                "specialty_name": (
                    doctor.specialty.name
                    if hasattr(doctor, "specialty")
                    and doctor.specialty is not None
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

        return {"items": items}