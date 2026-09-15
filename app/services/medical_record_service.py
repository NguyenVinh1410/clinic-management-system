from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import BusinessException, ConflictException, ForbiddenException, NotFoundException
from app.models.user import Doctor
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus
from app.models.medical_record import MedicalRecord
from app.models.working_schedule import WorkingSchedule
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordUpdate, MedicalRecordResponse


class MedicalRecordService:

    @staticmethod
    def get_record_by_id(
            db: Session,
            record_id: int
    ) -> MedicalRecord:

        stmt = (
            select(MedicalRecord)
            .where(MedicalRecord.record_id == record_id)
        )

        record = db.execute(stmt).scalar_one_or_none()

        if record is None:
            raise NotFoundException("Khong tim thay  ho so benh an")

        return record

    @staticmethod
    def get_record_by_appointment(
            db: Session,
            appointment_id: int
    ) -> MedicalRecord:

        stmt = (
            select(MedicalRecord)
            .options(
                selectinload(MedicalRecord.appointment)
                .selectinload(Appointment.schedule)
                .selectinload(WorkingSchedule.doctor)
                .selectinload(Doctor.specialty)
            )
            .where(MedicalRecord.appointment_id == appointment_id)
        )

        record = db.execute(stmt).scalars().first()

        if record is None:
            raise NotFoundException("Lich hen chua co ho so benh an")

        return MedicalRecordService.build_record_response(record)

    @staticmethod
    def get_all_records(db: Session) -> list[MedicalRecord]:

        stmt = (
            select(MedicalRecord)
            .order_by(MedicalRecord.examined_at.desc())
        )

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def get_appointment(
            db: Session,
            appointment_id: int
    ) -> Appointment:

        appointment = db.get(Appointment, appointment_id)

        if appointment is None:
            raise NotFoundException("Khong tim thay lich hen")

        return appointment

    @staticmethod
    def check_doctor_ownership(
            db: Session,
            appointment: Appointment,
            doctor_id: int
    ) -> None:

        stmt = (
            select(WorkingSchedule)
            .where(
                WorkingSchedule.schedule_id == appointment.schedule_id,
                WorkingSchedule.doctor_id == doctor_id
            )
        )

        schedule = db.execute(stmt).scalar_one_or_none()

        if schedule is None:
            raise ForbiddenException("Bac si khong phu trach lich hen nay")

    @staticmethod
    def get_record_existing(
            db: Session,
            appointment_id: int
    ) -> MedicalRecord | None:

        stmt = (
            select(MedicalRecord)
            .where(MedicalRecord.appointment_id == appointment_id)
        )

        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_patient_records(
            db:Session,
            patient_id: int
    ) -> list[MedicalRecordResponse]:

        stmt = (
            select(MedicalRecord)
            .join(
                Appointment,
                MedicalRecord.appointment_id == Appointment.appointment_id
            )
            .options(
                selectinload(MedicalRecord.appointment)
                .selectinload(Appointment.schedule)
                .selectinload(WorkingSchedule.doctor)
                .selectinload(Doctor.specialty)
            )
            .where(Appointment.patient_id == patient_id)
            .order_by(MedicalRecord.examined_at.desc())
        )

        records = db.execute(stmt).scalars().all()

        return [
            MedicalRecordService.build_record_response(record)
            for record in records
        ]

    @staticmethod
    def create_record(
            db: Session,
            data: MedicalRecordCreate,
            doctor_id: int
    ) -> MedicalRecord:

        appointment = MedicalRecordService.get_appointment(
            db=db,
            appointment_id=data.appointment_id
        )

        MedicalRecordService.check_doctor_ownership(
            db=db,
            appointment=appointment,
            doctor_id=doctor_id
        )

        if(appointment.status == AppointmentStatus.CANCELLED):
            raise BusinessException("Khong the tao ho so cho lich hen da huy")

        if (appointment.status != AppointmentStatus.CONFIRMED):
            raise BusinessException("Chi co the tao ho so sau khi lich hen duoc tiep nhan")

        existing_record = MedicalRecordService.get_record_existing(
            db=db,
            appointment_id=data.appointment_id
        )

        if existing_record is not None:
            raise ConflictException("Lich hen da co ho so benh an")

        if data.examined_at > datetime.now():
            raise BusinessException("Thoi gian kham khong duoc o tuong lai")

        record = MedicalRecord(
            appointment_id=data.appointment_id,
            symptoms=data.symptoms,
            diagnosis=data.diagnosis,
            note=data.note,
            examined_at=data.examined_at,
        )

        try:
            db.add(record)
            db.commit()
            db.refresh(record)

            return record

        except IntegrityError as exc:
            db.rollback()

            raise ConflictException("Lich hen da co ho so benh an") from exc

    @staticmethod
    def update_record(
            db: Session,
            record: MedicalRecord,
            data: MedicalRecordUpdate,
            doctor_id: int
    ) -> MedicalRecord:

        appointment = MedicalRecordService.get_appointment(
            db=db,
            appointment_id=record.appointment_id
        )

        MedicalRecordService.check_doctor_ownership(
            db=db,
            appointment=appointment,
            doctor_id=doctor_id
        )

        if appointment.status not in (
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.COMPLETED,
        ):
            raise BusinessException("Khong the sua ho so o trang thai hien tai")

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(record, field, value)

        db.commit()
        db.refresh(record)

        return record

    @staticmethod
    def build_record_response(record: MedicalRecord) -> MedicalRecordResponse:
        appointment = record.appointment

        doctor = appointment.schedule.doctor

        return MedicalRecordResponse(
            record_id=record.record_id,
            appointment_id=record.appointment_id,

            appointment_time=appointment.appointment_time,

            doctor_id=doctor.user_id,

            doctor_name=doctor.full_name,

            specialty_id=doctor.specialty_id,

            specialty_name=(
                doctor.specialty.name
                if doctor.specialty
                else None
            ),

            symptoms=record.symptoms,
            diagnosis=record.diagnosis,
            note=record.note,
            examined_at=record.examined_at,
        )