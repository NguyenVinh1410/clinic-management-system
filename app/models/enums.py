from enum import Enum

class UserRole(str, Enum):
    ADMIN = "Admin"
    RECEPTIONIST = "Receptionist"
    DOCTOR = "Doctor"
    PATIENT = "Patient"

class UserStatus(str, Enum):
    ACTIVE = "Active"
    LOCKED = "Locked"

class WorkingScheduleStatus(str, Enum):
    ACTIVE = "Active"
    OFF = "Off"

class AppointmentStatus(str, Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class AppointmentCreatedBy(str, Enum):
    PATIENT = "Patient"
    RECEPTIONIST = "Receptionist"
    AI = "AI"

class MedicineStatus(str, Enum):
    ACTIVE = "Active"
    DISCONTINUED = "Discontinued"

class InvoiceStatus(str, Enum):
    UNPAID = "Unpaid"
    PAID = "Paid"
    CANCELLED = "Cancelled"

class PaymentMethod(str, Enum):
    CASH = "Cash"
    ONLINE = "Online"

class ChatSenderType(str, Enum):
    PATIENT = "Patient"
    AI = "AI"

class PatientGender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"