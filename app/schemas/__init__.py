from app.schemas.auth import LoginRequest, TokenResponse, UserResponse, RegisterRequest

from app.schemas.patient import PatientResponse, PatientUpdate

from app.schemas.user import UserCreate

from app.schemas.specialty import SpecialtyResponse, SpecialtyUpdate, SpecialtyCreate

from app.schemas.doctor import DoctorResponse, DoctorUpdate

from app.schemas.working_schedule import WorkingScheduleResponse, WorkingScheduleUpdate, WorkingScheduleCreate

from app.schemas.appointment import AppointmentResponse, AppointmentUpdate, AppointmentCreate, AppointmentStatusUpdate

from app.schemas.medical_record import MedicalRecordResponse, MedicalRecordUpdate, MedicalRecordCreate

from app.schemas.medicine import MedicineResponse, MedicineUpdate, MedicineCreate

from app.schemas.prescription import PrescriptionResponse, PrescriptionDetailResponse, PrescriptionDetailCreate, PrescriptionCreate

from app.schemas.invoice import InvoiceResponse, InvoiceCreate, InvoicePaymentRequest

from app.schemas.dashboard import DashboardResponse, DashboardSummary, DoctorStatistic, MonthlyStatistic, MonthlyAppointmentStatistic, AppointmentStatusStatistic, SpecialtyStatistic

__all__ = ["LoginRequest",
           "TokenResponse",
           "UserResponse",
           "RegisterRequest",

           "PatientResponse",
           "PatientUpdate",

           "UserCreate",

           "SpecialtyResponse",
           "SpecialtyUpdate",
           "SpecialtyCreate",

           "DoctorResponse",
           "DoctorUpdate",

           "WorkingScheduleResponse",
           "WorkingScheduleUpdate",
           "WorkingScheduleCreate",

           "AppointmentResponse",
           "AppointmentUpdate",
           "AppointmentCreate",
           "AppointmentStatusUpdate",

           "MedicalRecordResponse",
           "MedicalRecordUpdate",
           "MedicalRecordCreate",

           "MedicineResponse",
           "MedicineUpdate",
           "MedicineCreate",

           "PrescriptionResponse",
           "PrescriptionDetailResponse",
           "PrescriptionDetailCreate",
           "PrescriptionCreate",

           "InvoiceResponse",
           "InvoiceCreate",
           "InvoicePaymentRequest",

           "DashboardResponse",
           "DashboardSummary",
           "DoctorStatistic",
           "MonthlyStatistic",
           "MonthlyAppointmentStatistic",
           "AppointmentStatusStatistic",
           "SpecialtyStatistic",

           ]