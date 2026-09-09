from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus, InvoiceStatus
from app.models.invoice import Invoice
from app.models.user import Doctor, Patient
from app.models.working_schedule import WorkingSchedule
from app.models.specialty import Specialty


class DashboardService:

    @staticmethod
    def get_summary(db: Session):
        total_patients = db.scalar(select(func.count(Patient.user_id))) or 0

        today = date.today()

        today_appointments = (
                db.scalar(
                    select(func.count(Appointment.appointment_id))
                    .join(
                        WorkingSchedule,
                        Appointment.schedule_id == WorkingSchedule.schedule_id
                    )
                    .where(WorkingSchedule.work_date == today)
                )
                or 0
        )
        pending_appointments = (
                db.scalar(
                    select(func.count(Appointment.appointment_id))
                    .where(Appointment.status == AppointmentStatus.PENDING)
                )
                or 0
        )
        current_year = today.year
        current_month = today.month

        monthly_revenue = (
                db.scalar(
                    select(func.coalesce(func.sum(Invoice.total_amount), 0, ))
                    .where(
                        Invoice.status == InvoiceStatus.PAID,
                        func.year(Invoice.paid_at) == current_year,
                        func.month(Invoice.paid_at) == current_month,
                    )
                )
                or Decimal("0.00")
        )

        return {
            "total_patients": total_patients,
            "today_appointments": today_appointments,
            "monthly_revenue": monthly_revenue,
            "pending_appointments": pending_appointments,
        }

    @staticmethod
    def get_appointments_by_month(db: Session):
        stmt = (
            select(
                func.date_format(
                    WorkingSchedule.work_date,
                    "%Y-%m",
                ).label("month"),

                func.count(Appointment.appointment_id).label("total")
            )
            .join(
                WorkingSchedule,
                Appointment.schedule_id == WorkingSchedule.schedule_id
            )
            .group_by(
                func.date_format(
                    WorkingSchedule.work_date,
                    "%Y-%m",
                )
            )
            .order_by(
                func.date_format(
                    WorkingSchedule.work_date,
                    "%Y-%m",
                )
            )
        )

        rows = db.execute(stmt).all()

        return [
            {
                "month": row.month,
                "total": row.total,
            }
            for row in rows
        ]

    @staticmethod
    def get_revenue_by_month(db: Session):
        stmt = (
            select(
                func.date_format(
                    Invoice.paid_at,
                    "%Y-%m",
                ).label("month"),

                func.sum(Invoice.total_amount).label("value")
            )
            .where(
                Invoice.status == InvoiceStatus.PAID,
                Invoice.paid_at.is_not(None),
            )
            .group_by(
                func.date_format(
                    Invoice.paid_at,
                    "%Y-%m",
                )
            )
            .order_by(
                func.date_format(
                    Invoice.paid_at,
                    "%Y-%m",
                )
            )
        )

        rows = db.execute(stmt).all()

        return [
            {
                "month": row.month,
                "value": row.value or Decimal("0.00"),
            }
            for row in rows
        ]

    @staticmethod
    def get_appointments_by_specialty(db: Session):
        stmt = (
            select(
                Specialty.specialty_id,

                Specialty.name.label("specialty_name"),

                func.count(Appointment.appointment_id).label("total"),
            )
            .join(
                Doctor,
                Doctor.specialty_id == Specialty.specialty_id
            )
            .join(
                WorkingSchedule,
                WorkingSchedule.doctor_id == Doctor.user_id,
            )
            .join(
                Appointment,
                Appointment.schedule_id == WorkingSchedule.schedule_id,
            )
            .group_by(
                Specialty.specialty_id,
                Specialty.name,
            )
            .order_by(
                func.count(Appointment.appointment_id).desc()
            )
        )

        rows = db.execute(stmt).all()

        return [
            {
                "specialty_id": row.specialty_id,
                "specialty_name": row.specialty_name,
                "total": row.total,
            }
            for row in rows
        ]
    @staticmethod
    def get_top_doctors(db: Session):
        stmt = (
            select(
                Doctor.user_id.label("doctor_id"),
                Doctor.full_name.label("doctor_name"),
                func.count(Appointment.appointment_id).label("total"),
            )
            .join(
                WorkingSchedule,
                WorkingSchedule.doctor_id == Doctor.user_id,
            )
            .join(
                Appointment,
                Appointment.schedule_id == WorkingSchedule.schedule_id,
            )
            .where(
                Appointment.status == AppointmentStatus.COMPLETED,
            )
            .group_by(
                Doctor.user_id,
                Doctor.full_name,
            )
            .order_by(
                func.count(Appointment.appointment_id).desc()
            )
            .limit(10)
        )

        rows = db.execute(stmt).all()

        return [
            {
                "doctor_id": row.doctor_id,
                "doctor_name": row.doctor_name,
                "total": row.total,
            }
            for row in rows
        ]

    @staticmethod
    def get_appointments_by_status(db: Session):
        stmt = (
            select(
                Appointment.status.label("status"),
                func.count(Appointment.appointment_id).label("total"),
            )
            .group_by(
                Appointment.status
            )
            .order_by(
                Appointment.status
            )
        )

        rows = db.execute(stmt).all()

        return [
            {
                "status": (
                    row.status.value
                    if hasattr(row.status, "value")
                    else str(row.status)
                ),
                "total": row.total,
            }
            for row in rows
        ]

    @staticmethod
    def get_dashboard(db: Session):
        return {
            "summary": DashboardService.get_summary(db),
            "appointments_by_month": DashboardService.get_appointments_by_month(db),
            "revenue_by_month": DashboardService.get_revenue_by_month(db),
            "appointments_by_specialty": DashboardService.get_appointments_by_specialty(db),
            "top_doctors": DashboardService.get_top_doctors(db),
            "appointments_by_status": DashboardService.get_appointments_by_status(db),
        }
