from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BusinessException, ConflictException, NotFoundException
from app.models.enums import AppointmentStatus, AppointmentCreatedBy, UserRole, UserStatus, WorkingScheduleStatus
from app.models.user import User, Doctor, Patient
from app.models.working_schedule import WorkingSchedule
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.models.chat import ChatSession


class AppointmentService:
    APPOINTMENT_DURATION_MINUTES = 30

    @staticmethod
    def get_appointment_by_id(
            db: Session,
            appointment_id: int
    ) -> Appointment:

        stmt = (
            select(Appointment)
            .options(
                joinedload(Appointment.schedule)
                .joinedload(WorkingSchedule.doctor)
                .joinedload(Doctor.specialty)
            )
            .where(Appointment.appointment_id == appointment_id)
        )

        appointment = db.execute(stmt).scalar_one_or_none()

        if appointment is None:
            raise NotFoundException("Khong tim thay lich hen")

        return appointment

    @staticmethod
    def get_all_appointments(
            db: Session,
    ) -> list[dict]:

        stmt = (
            select(Appointment)
            .options(
                joinedload(Appointment.schedule)
                .joinedload(WorkingSchedule.doctor)
                .joinedload(Doctor.specialty)
            )
            .order_by(Appointment.appointment_time)
        )

        appointments = db.execute(stmt).scalars().all()

        return [
            AppointmentService._appointment_to_response(appointment)
            for appointment in appointments
        ]

    @staticmethod
    def get_appointments_by_patient(
            db: Session,
            patient_id: int
    ) -> list[dict]:

        patient = db.get(Patient, patient_id)

        if patient is None:
            raise NotFoundException("Khong tim thay benh nhan")

        stmt = (
            select(Appointment)
            .options(
                joinedload(Appointment.schedule)
                .joinedload(WorkingSchedule.doctor)
                .joinedload(Doctor.specialty)
            )
            .where(Appointment.patient_id == patient_id)
            .order_by(Appointment.appointment_time.desc())
        )

        appointments = db.execute(stmt).scalars().all()

        return [
            AppointmentService._appointment_to_response(appointment)
            for appointment in appointments
        ]

    @staticmethod
    def get_appointments_by_doctor(
            db: Session,
            doctor_id: int
    ) -> list[dict]:

        doctor = db.get(Doctor, doctor_id)

        if doctor is None:
            raise NotFoundException("Khong tim thay bac si")

        stmt = (
            select(Appointment)
            .join(
                WorkingSchedule,
                Appointment.schedule_id == WorkingSchedule.schedule_id
            )
            .options(
                joinedload(Appointment.schedule)
                .joinedload(WorkingSchedule.doctor)
                .joinedload(Doctor.specialty)
            )
            .where(WorkingSchedule.doctor_id == doctor_id)
            .order_by(Appointment.appointment_time)
        )

        appointments = db.execute(stmt).scalars().all()

        return [
            AppointmentService._appointment_to_response(appointment)
            for appointment in appointments
        ]

    @staticmethod
    def validate_patient(
            db: Session,
            patient_id: int
    ) -> Patient:

        patient = db.get(Patient, patient_id)

        if patient is None:
            raise NotFoundException("Khong tim thay benh nhan")

        if patient.status != UserStatus.ACTIVE:
            raise BusinessException("Tai khoan benh nhan khong hoat dong")

        return patient

    @staticmethod
    def validate_schedule(
            db: Session,
            schedule_id: int
    ) -> WorkingSchedule:

        schedule = db.get(WorkingSchedule, schedule_id)

        if schedule is None:
            raise NotFoundException("Khong tim thay ca lam viec")

        if schedule.status != WorkingScheduleStatus.ACTIVE:
            raise BusinessException("Ca lam viec khong hoat dong")

        return schedule

    @staticmethod
    def validate_appointment_time(
            schedule: WorkingSchedule,
            appointment_time: datetime
    ) -> None:

        if appointment_time < datetime.now():
            raise BusinessException("Khong the dat lich trong qua khu")

        if appointment_time.date() != schedule.work_date:
            raise BusinessException("Thoi gian kham khong thuoc ngay cua ca lam viec")

        appointment_time_only = appointment_time.time()

        appointment_end = appointment_time + timedelta(minutes=AppointmentService.APPOINTMENT_DURATION_MINUTES)

        if appointment_time_only < schedule.start_time:
            raise BusinessException("Thoi gian kham phai nam trong ca lam viec cua bac si")

        schedule_end = datetime.combine(
            schedule.work_date,
            schedule.end_time
        )

        if appointment_end > schedule_end:
            raise BusinessException("Luot kham 30p vuot qua thoi gian ca lam viec")

        schedule_start = datetime.combine(
            schedule.work_date,
            schedule.start_time
        )

        elapsed_seconds = (appointment_time - schedule_start).total_seconds()

        slot_seconds = AppointmentService.APPOINTMENT_DURATION_MINUTES * 60

        if elapsed_seconds % slot_seconds != 0:
            raise BusinessException("Thoi gian kham phai theo khung 30p")

    @staticmethod
    def check_duplicate_appointment(
            db: Session,
            schedule: WorkingSchedule,
            appointment_time: datetime,
            patient_id: int,
            exclude_appointment_id: int | None = None
    ) -> None:

        appointment_end = appointment_time + timedelta(minutes=AppointmentService.APPOINTMENT_DURATION_MINUTES)

        doctor_stmt = (
            select(Appointment)
            .join(
                WorkingSchedule,
                Appointment.schedule_id == WorkingSchedule.schedule_id
            )
            .where(
                WorkingSchedule.doctor_id == schedule.doctor_id,
                Appointment.status.in_(
                    [
                        AppointmentStatus.PENDING,
                        AppointmentStatus.CONFIRMED
                    ]
                ),
                Appointment.appointment_time < appointment_end,
                (
                    Appointment.appointment_time + timedelta(minutes=AppointmentService.APPOINTMENT_DURATION_MINUTES)
                )
                > appointment_time,
            )
        )

        if exclude_appointment_id is not None:
            doctor_stmt = doctor_stmt.where(Appointment.appointment_id != exclude_appointment_id)

        existing_doctor_appointment = db.execute(doctor_stmt).scalar_one_or_none()

        if existing_doctor_appointment is not None:
            raise ConflictException("Bac si da co lich hen vao thoi gian nay")

        patient_stmt = (
            select(Appointment)
            .where(
                Appointment.patient_id == patient_id,
                Appointment.status.in_(
                    [
                        AppointmentStatus.PENDING,
                        AppointmentStatus.CONFIRMED
                    ]
                ),
                Appointment.appointment_time < appointment_end,
                Appointment.appointment_time >= (appointment_time - timedelta(minutes=AppointmentService.APPOINTMENT_DURATION_MINUTES))
                #Appointment.appointment_time + timedelta(minutes=AppointmentService.APPOINTMENT_DURATION_MINUTES) > appointment_time,
            )
        )

        if exclude_appointment_id is not None:
            patient_stmt = patient_stmt.where(Appointment.appointment_id != exclude_appointment_id)

        existing_patient_appointment = db.execute(patient_stmt).scalar_one_or_none()

        if existing_patient_appointment is not None:
            raise ConflictException("Benh nhan da co lich hen vao thoi gian nay")

    @staticmethod
    def create_appointment(
            db: Session,
            data: AppointmentCreate,
            current_user: User
    ) -> Appointment:

        if current_user.role == UserRole.PATIENT:
            patient_id = current_user.user_id

            created_by = AppointmentCreatedBy.PATIENT

        elif current_user.role == UserRole.RECEPTIONIST:
            if data.patient_id is None:
                raise BusinessException("Le tan phai cung cap patient_id")

            patient_id = data.patient_id

            created_by = AppointmentCreatedBy.RECEPTIONIST

        else:
            raise BusinessException("Ban khong co quyen tao lich hen")

        AppointmentService.validate_patient(db=db, patient_id=patient_id)

        schedule = AppointmentService.validate_schedule(
            db=db,
            schedule_id=data.schedule_id,
        )

        doctor = db.get(
            Doctor,
            schedule.doctor_id,
        )

        if doctor is None:
            raise NotFoundException("Khong tim thay bac si cua ca lam viec")

        AppointmentService.validate_appointment_time(
            schedule=schedule,
            appointment_time=data.appointment_time,
        )

        AppointmentService.check_duplicate_appointment(
            db=db,
            schedule=schedule,
            appointment_time=data.appointment_time,
            patient_id=patient_id,
        )

        appointment = Appointment(
            schedule_id=data.schedule_id,
            patient_id=patient_id,
            appointment_time=data.appointment_time,
            status=AppointmentStatus.PENDING,
            created_by=created_by,
            note=data.note,
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        return appointment

    @staticmethod
    def create_appointment_by_ai(
            db: Session,
            patient_id: int,
            schedule_id: int,
            appointment_time: datetime,
            chat_session_id: int,
    ) -> Appointment:

        AppointmentService.validate_patient(
            db=db,
            patient_id=patient_id,
        )

        schedule = AppointmentService.validate_schedule(
            db=db,
            schedule_id=schedule_id,
        )

        doctor = db.get(
            Doctor,
            schedule.doctor_id,
        )

        if doctor is None:
            raise NotFoundException(
                "Khong tim thay bac si cua ca lam viec"
            )

        chat_session = db.get(
            ChatSession,
            chat_session_id,
        )

        if chat_session is None:
            raise NotFoundException(
                "Khong tim thay phien tro chuyen"
            )

        if chat_session.patient_id != patient_id:
            raise BusinessException(
                "Phien tro chuyen khong thuoc benh nhan hien tai"
            )

        if chat_session.appointment is not None:
            raise ConflictException(
                "Phien tro chuyen nay da duoc gan voi lich hen"
            )

        AppointmentService.validate_appointment_time(
            schedule=schedule,
            appointment_time=appointment_time,
        )

        AppointmentService.check_duplicate_appointment(
            db=db,
            schedule=schedule,
            appointment_time=appointment_time,
            patient_id=patient_id,
        )

        appointment = Appointment(
            schedule_id=schedule_id,
            patient_id=patient_id,
            chat_session_id=chat_session_id,
            appointment_time=appointment_time,
            status=AppointmentStatus.PENDING,
            created_by=AppointmentCreatedBy.AI,
            note="Dat lich thong qua AI Assistant",
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        return appointment

    @staticmethod
    def update_appointment(
            db: Session,
            appointment: Appointment,
            data: AppointmentUpdate
    ) -> Appointment:
        if appointment.status in (
                AppointmentStatus.COMPLETED,
                AppointmentStatus.CANCELLED,
        ):
            raise BusinessException("Khong the cap nhat lich hen da hoan tat hoac da huy")

        update_data = data.model_dump(exclude_unset=True)

        new_appointment_time = update_data.get(
            'appointment_time',
            appointment.appointment_time,
        )

        if (new_appointment_time != appointment.appointment_time):
            schedule = (
                AppointmentService.validate_schedule(
                    db=db,
                    schedule_id=appointment.schedule_id,
                )
            )

            AppointmentService.validate_appointment_time(
                schedule=schedule,
                appointment_time=new_appointment_time,
            )

            AppointmentService.check_duplicate_appointment(
                db=db,
                schedule=schedule,
                appointment_time=new_appointment_time,
                patient_id=appointment.patient_id,
                exclude_appointment_id=appointment.appointment_id
            )

        allowed_fields = {
            'appointment_time',
            'note'
        }

        for field, value in update_data.items():
            if field not in allowed_fields:
                continue

            setattr(appointment, field, value)

        db.commit()
        db.refresh(appointment)

        return appointment

    @staticmethod
    def update_status(
            db: Session,
            appointment: Appointment,
            new_status: AppointmentStatus
    ) -> Appointment:

        current_status = appointment.status

        if current_status == new_status:
            return appointment

        if current_status == AppointmentStatus.PENDING:
            if new_status not in (
                    AppointmentStatus.CONFIRMED,
                    AppointmentStatus.CANCELLED,
            ):
                raise BusinessException("Pending chi co the chuyen qua Confirmed hoac Cancelled")

        elif current_status == AppointmentStatus.CONFIRMED:
            if new_status not in (
                    AppointmentStatus.COMPLETED,
                    AppointmentStatus.CANCELLED,
            ):
                raise BusinessException("Confirmed chi co the chuyen sang Completed hoac Cancelled")

        elif current_status == AppointmentStatus.COMPLETED:
            raise BusinessException("Lich da hoan tat, khong the thay doi trang thai")

        elif current_status == AppointmentStatus.CANCELLED:
            raise BusinessException("Lich da huy, khong the khoi phuc")

        appointment.status = new_status

        db.commit()
        db.refresh(appointment)

        return appointment

    @staticmethod
    def cancel_appointment(
            db: Session,
            appointment: Appointment,
    ) -> Appointment:

        if appointment.status == AppointmentStatus.COMPLETED:
            raise BusinessException("Khong the huy lich da hoan tat")

        if appointment.status == AppointmentStatus.CANCELLED:
            return appointment

        appointment.status = AppointmentStatus.CANCELLED

        db.commit()
        db.refresh(appointment)

        return appointment

    @staticmethod
    def cancel_appointment_by_ai(
            db: Session,
            appointment_id: int,
            patient_id: int,
    ) -> Appointment:

        appointment = (
            AppointmentService.get_appointment_by_id(
                db=db,
                appointment_id=appointment_id,
            )
        )

        if appointment.patient_id != patient_id:
            raise BusinessException(
                "Lich hen nay khong thuoc benh nhan hien tai"
            )

        if appointment.status == AppointmentStatus.COMPLETED:
            raise BusinessException(
                "Khong the huy lich da hoan tat"
            )

        if appointment.status == AppointmentStatus.CANCELLED:
            raise BusinessException(
                "Lich hen nay da duoc huy"
            )

        appointment.status = AppointmentStatus.CANCELLED

        db.commit()
        db.refresh(appointment)

        return appointment

    @staticmethod
    def belong_to_doctor(
            db: Session,
            appointment: Appointment,
            doctor_id: int
    ) -> bool:

        stmt = (
            select(Appointment)
            .join(
                WorkingSchedule,
                Appointment.schedule_id == WorkingSchedule.schedule_id,
            )
            .where(
                Appointment.appointment_id == appointment.appointment_id,
                WorkingSchedule.doctor_id == doctor_id,
            )
        )

        return db.execute(stmt).scalar_one_or_none() is not None

    @staticmethod
    def check_in_appointment(
            db: Session,
            appointment: Appointment,
    ) -> Appointment:

        today = datetime.now().date()

        if appointment.appointment_time.date() != today:
            raise BusinessException("Chi co the tiep nhan benh nhan co lich trong hom nay")

        if appointment.status != AppointmentStatus.PENDING:
            if appointment.status == AppointmentStatus.CONFIRMED:
                raise ConflictException("Lich hen nay da duoc tiep nhan")

            if appointment.status == AppointmentStatus.COMPLETED:
                raise BusinessException("Lich hen da hoan thanh")

            if appointment.status == AppointmentStatus.CANCELLED:
                raise BusinessException("Lich hen da bi huy")

            raise BusinessException("Khong the tiep nhan lich hen nay")

        appointment.status = AppointmentStatus.CONFIRMED

        db.commit()
        db.refresh(appointment)

        return appointment

    @staticmethod
    def _appointment_to_response(
            appointment: Appointment,
    ) -> dict:

        schedule = appointment.schedule
        doctor = schedule.doctor

        return {
            "appointment_id": appointment.appointment_id,

            "schedule_id": appointment.schedule_id,

            "patient_id": appointment.patient_id,

            "patient_name": appointment.patient.full_name,

            "patient_phone": appointment.patient.phone,

            "chat_session_id": appointment.chat_session_id,

            "appointment_time": appointment.appointment_time,

            "status": appointment.status,

            "created_by": appointment.created_by,

            "note": appointment.note,

            "doctor_id": doctor.user_id,

            "doctor_name": doctor.full_name,

            "specialty_id": doctor.specialty_id,

            "specialty_name": (
                doctor.specialty.name
                if doctor.specialty.name is not None
                else ""
            ),
        }