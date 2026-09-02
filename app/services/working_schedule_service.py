from datetime import date, time

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessException, ConflictException, NotFoundException
from app.models.enums import UserStatus, WorkingScheduleStatus
from app.models.user import Doctor
from app.models.working_schedule import WorkingSchedule
from app.schemas.working_schedule import WorkingScheduleCreate, WorkingScheduleUpdate


class WorkingScheduleService:

    @staticmethod
    def get_all_schedules(
            db: Session,
    ) -> list[WorkingSchedule]:

        stmt = (
            select(WorkingSchedule)
            .order_by(
                WorkingSchedule.work_date,
                WorkingSchedule.start_time,
            )
        )

        return list(
            db.execute(stmt).scalars().all()
        )

    @staticmethod
    def get_schedule_by_id(
            db: Session,
            schedule_id: int,
    ) -> WorkingSchedule:

        stmt = (
            select(WorkingSchedule)
            .where(WorkingSchedule.schedule_id == schedule_id)
        )

        schedule = db.execute(stmt).scalar_one_or_none()

        if schedule is None:
            raise NotFoundException("Khong tim thay lich lam viec")

        return schedule

    @staticmethod
    def get_schedule_by_doctor(
            db: Session,
            doctor_id: int,
    ) -> list[WorkingSchedule]:

        doctor = db.get(
            Doctor,
            doctor_id
        )

        if doctor is None:
            raise NotFoundException("Khong tim thay bac si")

        stmt = (
            select(WorkingSchedule)
            .where(WorkingSchedule.doctor_id == doctor_id)
            .order_by(
                WorkingSchedule.work_date,
                WorkingSchedule.start_time,
            )
        )

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def validate_doctor(
            db: Session,
            doctor_id: int,
    ) -> Doctor:

        doctor = db.get(
            Doctor,
            doctor_id
        )

        if doctor is None:
            raise NotFoundException("Khong tim thay bac si")

        if doctor.status != UserStatus.ACTIVE:
            raise BusinessException("Bac si khong hoat dong")

        return doctor

    @staticmethod
    def validate_work_date(
            work_date: date
    ) -> None:

        if work_date < date.today():
            raise BusinessException("Khong the tao hoac cap nhat lich lam viec trong qua khu")

    @staticmethod
    def check_overlap(
            db: Session,
            doctor_id: int,
            work_date: date,
            start_time: time,
            end_time: time,
            exclude_schedule_id: int | None = None,
    ) -> None:

        stmt = (
            select(WorkingSchedule)
            .where(
                WorkingSchedule.doctor_id == doctor_id,
                WorkingSchedule.work_date == work_date,
                WorkingSchedule.status == WorkingScheduleStatus.ACTIVE,
                WorkingSchedule.start_time < end_time,
                WorkingSchedule.end_time > start_time,
            )
        )

        if exclude_schedule_id is not None:
            stmt = stmt.where(WorkingSchedule.schedule_id != exclude_schedule_id)

        existing_schedule = (db.execute(stmt).scalars().first())

        if existing_schedule is not None:
            raise ConflictException("Lich lam viec bi trung voi lich hien tai cua bac si")

    @staticmethod
    def create_schedule(
            db: Session,
            data: WorkingScheduleCreate,
    ) -> WorkingSchedule:

        WorkingScheduleService.validate_doctor(
            db=db,
            doctor_id=data.doctor_id,
        )

        WorkingScheduleService.validate_work_date(data.work_date)

        WorkingScheduleService.check_overlap(
            db=db,
            doctor_id=data.doctor_id,
            work_date=data.work_date,
            start_time=data.start_time,
            end_time=data.end_time,
        )

        schedule = WorkingSchedule(
            doctor_id=data.doctor_id,
            work_date=data.work_date,
            start_time=data.start_time,
            end_time=data.end_time,
            status=data.status,
        )

        try:
            db.add(schedule)
            db.commit()
            db.refresh(schedule)

            return schedule

        except IntegrityError as exc:

            db.rollback()

            raise ConflictException("Lich lam viec bi trung") from exc

    @staticmethod
    def update_schedule(
            db: Session,
            schedule: WorkingSchedule,
            data: WorkingScheduleUpdate
    ) -> WorkingSchedule:

        update_data = data.model_dump(exclude_unset=True)

        new_work_date = update_data.get(
            "work_date",
            schedule.work_date
        )

        new_start_time = update_data.get(
            "start_time",
            schedule.start_time
        )

        new_end_time = update_data.get(
            "end_time",
            schedule.end_time
        )

        new_status = update_data.get(
            "status",
            schedule.status
        )

        WorkingScheduleService.validate_work_date(new_work_date)

        if new_start_time >= new_end_time:
            raise BusinessException("Start time phai nho hon end time")

        if new_status == WorkingScheduleStatus.ACTIVE:
            WorkingScheduleService.check_overlap(
                db=db,
                doctor_id=schedule.doctor_id,
                work_date=new_work_date,
                start_time=new_start_time,
                end_time=new_end_time,
                exclude_schedule_id=schedule.schedule_id,
            )

        for field, value in update_data.items():
            setattr(schedule, field, value)

        try:
            db.commit()
            db.refresh(schedule)

            return schedule
        except IntegrityError as exc:
            raise ConflictException("Khong the cap nhat lich lam viec") from exc

    @staticmethod
    def delete_schedule(
            db: Session,
            schedule: WorkingSchedule
    ) -> None:

        if schedule.appointment:
            raise ConflictException("Khong the xoa lich vi da co lich hen")

        try:
            db.delete(schedule)
            db.commit()

        except IntegrityError as exc:
            db.rollback()
            raise ConflictException("Khong the xoa lich lam viec") from exc

        