from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException, ConflictException, NotFoundException
from app.models.enums import AppointmentStatus, AppointmentCreatedBy, UserRole, UserStatus, WorkingScheduleStatus
from app.models.user import User, Doctor, Patient
from app.models.working_schedule import WorkingSchedule
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate

class AppointmentService:
    @staticmethod
    def get_appointment_by_id(
            db: Session,
            appointment_id: int
    ) -> Appointment:

        stmt = (
            select(Appointment)
            .where(Appointment.appointment_id == appointment_id)
        )

        appointment = db.execute(stmt).scalar_one_or_none()

        if appointment is None:
            raise NotFoundException("Khong tim thay lich hen")

        return appointment

    @staticmethod
    def get_all_appointments(
            db: Session,
    ) -> list[Appointment]:

        stmt = (
            select(Appointment)
            .order_by(Appointment.appointment_time)
        )

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def get_appointments_by_patient(
            db: Session,
            patient_id: int
    ) -> list[Appointment]:

        patient = db.get(Patient, patient_id)

        if patient is None:
            raise NotFoundException("Khong tim thay benh nhan")

        stmt = (
            select(Appointment)
            .where(Appointment.patient_id == patient_id)
            .order_by(Appointment.appointment_time.desc())
        )

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def get_appointments_by_doctor(
            db: Session,
            doctor_id: int
    ) -> list[Appointment]:

        doctor = db.get(Doctor, doctor_id)

        if doctor is None:
            raise NotFoundException("Khong tim thay bac si")

        stmt = (
            select(Appointment)
            .join(
                WorkingSchedule,
                Appointment.schedule_id == WorkingSchedule.schedule_id
            )
            .where(WorkingSchedule.doctor_id == doctor_id)
            .order_by(Appointment.appointment_time)
        )
        return list(db.execute(stmt).scalars().all())

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

        appointment_time_only = (appointment_time.time())

        if not (
            schedule.start_time <= appointment_time_only <= schedule.end_time
        ):
            raise BusinessException("Thoi gian kham phai nam trong ca lam viec cua bac si")

    @staticmethod
    def check_duplicate_appointment(
            db: Session,
            schedule: WorkingSchedule,
            appointment_time: datetime,
            patient_id: int
    ) -> None:

        doctor_stmt = (
            select(Appointment)
            .join(
                WorkingSchedule,
                Appointment.schedule_id == WorkingSchedule.schedule_id
            )
            .where(
                WorkingSchedule.doctor_id == schedule.doctor_id,
                Appointment.appointment_time == appointment_time,
                Appointment.status.in_(
                    [
                        AppointmentStatus.PENDING,
                        AppointmentStatus.CONFIRMED
                    ]
                ),
            )
        )

        existing_doctor_appointment = db.execute(doctor_stmt).scalar_one_or_none()

        if existing_doctor_appointment is not None:
            raise ConflictException("Bac si da co lich hen vao thoi gian nay")

        patient_stmt = (
            select(Appointment)
            .where(
                Appointment.patient_id == patient_id,
                Appointment.appointment_time == appointment_time,
                Appointment.status.in_(
                    [
                        AppointmentStatus.PENDING,
                        AppointmentStatus.CONFIRMED
                    ]
                )
            )
        )

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

        schedule = (AppointmentService.validate_schedule(
            db=db,
            schedule_id=data.patient_id,
        ))

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

        if(new_appointment_time != appointment.appointment_time):
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
                patient_id=appointment.appointment_id,
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