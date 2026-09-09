from decimal import Decimal

from pydantic import BaseModel

class DashboardSummary(BaseModel):
    total_patients: int
    today_appointments: int
    monthly_revenue: Decimal
    pending_appointments: int

class MonthlyStatistic(BaseModel):
    month: str
    value: Decimal

class MonthlyAppointmentStatistic(BaseModel):
    month: str
    total: int

class SpecialtyStatistic(BaseModel):
    specialty_id: int
    specialty_name: str
    total: int

class DoctorStatistic(BaseModel):
    doctor_id: int
    doctor_name: str
    total: int

class AppointmentStatusStatistic(BaseModel):
    status: str
    total: int

class DashboardResponse(BaseModel):
    summary: DashboardSummary

    appointments_by_month: list[MonthlyAppointmentStatistic]

    revenue_by_month: list[MonthlyStatistic]

    appointments_by_specialty: list[SpecialtyStatistic]

    top_doctors: list[DoctorStatistic]

    appointments_by_status: list[AppointmentStatusStatistic]


