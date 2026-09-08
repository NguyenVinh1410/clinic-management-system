from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException, ConflictException, ForbiddenException, NotFoundException
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus
from app.models.medical_record import MedicalRecord
from app.models.working_schedule import WorkingSchedule
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordUpdate

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
            .where(MedicalRecord.appointment_id == appointment_id)
        )

        record = db.execute(stmt).scalar_one_or_none()

        if record is None:
            raise NotFoundException("Lich hen chua co ho so benh an")

        return record

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

        if (appointment.status != AppointmentStatus.COMPLETED):
            raise BusinessException("Chi co the tao ho so sau khi kham xong")

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

        if (appointment.status == AppointmentStatus.CANCELLED):
            raise BusinessException("Khong the sua ho so cua lich hen da huy")

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(record, field, value)

        db.commit()
        db.refresh(record)

        return record