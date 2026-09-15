from __future__ import annotations

import argparse
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.database.connection import SessionLocal
from app.models import (
    Admin,
    Appointment,
    ChatMessage,
    ChatSession,
    Doctor,
    Invoice,
    MedicalRecord,
    Medicine,
    Patient,
    Prescription,
    PrescriptionDetail,
    Receptionist,
    Specialty,
    User,
    WorkingSchedule,
)
from app.models.enums import (
    AppointmentCreatedBy,
    AppointmentStatus,
    ChatSenderType,
    Gender,
    InvoiceStatus,
    MedicineStatus,
    PaymentMethod,
    UserRole,
    UserStatus,
    WorkingScheduleStatus,
)


# ============================================================
# CONFIG
# ============================================================

CONSULTATION_FEE = Decimal("100000.00")


PASSWORDS = {
    "admin": "Admin123",
    "admin02": "Admin123",

    "receptionist01": "Reception123",
    "receptionist02": "Reception123",

    "doctor01": "Doctor123",
    "doctor02": "Doctor123",
    "doctor03": "Doctor123",
    "doctor04": "Doctor123",
    "doctor05": "Doctor123",
    "doctor06": "Doctor123",

    "patient01": "Patient123",
    "patient02": "Patient123",
    "patient03": "Patient123",
    "patient04": "Patient123",
    "patient05": "Patient123",
    "patient06": "Patient123",
    "patient07": "Patient123",
    "patient08": "Patient123",
    "patient09": "Patient123",
    "patient10": "Patient123",
    "patient11": "Patient123",
    "patient12": "Patient123",
}


# ============================================================
# BASIC HELPERS
# ============================================================

def get_user(
    db: Session,
    username: str,
) -> User | None:

    return db.execute(
        select(User).where(
            User.username == username
        )
    ).scalar_one_or_none()


def get_or_create_specialty(
    db: Session,
    *,
    name: str,
    description: str,
) -> tuple[Specialty, bool]:

    specialty = db.execute(
        select(Specialty).where(
            Specialty.name == name
        )
    ).scalar_one_or_none()

    if specialty is not None:
        return specialty, False

    specialty = Specialty(
        name=name,
        description=description,
    )

    db.add(specialty)
    db.flush()

    return specialty, True


def get_or_create_medicine(
    db: Session,
    *,
    name: str,
    unit: str,
    price: Decimal,
    stock_qty: int,
    status: MedicineStatus = MedicineStatus.ACTIVE,
) -> tuple[Medicine, bool]:

    medicine = db.execute(
        select(Medicine).where(
            Medicine.name == name
        )
    ).scalar_one_or_none()

    if medicine is not None:
        return medicine, False

    medicine = Medicine(
        name=name,
        unit=unit,
        price=price,
        stock_qty=stock_qty,
        status=status,
    )

    db.add(medicine)
    db.flush()

    return medicine, True


# ============================================================
# USERS
# ============================================================

def get_or_create_admin(
    db: Session,
    *,
    username: str,
    full_name: str,
    email: str,
    phone: str,
    gender: Gender,
    status: UserStatus = UserStatus.ACTIVE,
) -> Admin:

    existing = get_user(
        db,
        username,
    )

    if existing is not None:
        if not isinstance(existing, Admin):
            raise RuntimeError(
                f"Username '{username}' khong phai Admin"
            )

        return existing

    admin = Admin(
        username=username,
        password=hash_password(
            PASSWORDS[username]
        ),
        full_name=full_name,
        email=email,
        phone=phone,
        gender=gender,
        role=UserRole.ADMIN,
        status=status,
        type="admin",
    )

    db.add(admin)
    db.flush()

    return admin


def get_or_create_receptionist(
    db: Session,
    *,
    username: str,
    full_name: str,
    email: str,
    phone: str,
    gender: Gender,
    status: UserStatus = UserStatus.ACTIVE,
) -> Receptionist:

    existing = get_user(
        db,
        username,
    )

    if existing is not None:
        if not isinstance(existing, Receptionist):
            raise RuntimeError(
                f"Username '{username}' khong phai Receptionist"
            )

        return existing

    receptionist = Receptionist(
        username=username,
        password=hash_password(
            PASSWORDS[username]
        ),
        full_name=full_name,
        email=email,
        phone=phone,
        gender=gender,
        role=UserRole.RECEPTIONIST,
        status=status,
        type="receptionist",
    )

    db.add(receptionist)
    db.flush()

    return receptionist


def get_or_create_doctor(
    db: Session,
    *,
    username: str,
    full_name: str,
    email: str,
    phone: str,
    gender: Gender,
    specialty_id: int,
    qualification: str,
    bio: str,
    status: UserStatus = UserStatus.ACTIVE,
) -> Doctor:

    existing = get_user(
        db,
        username,
    )

    if existing is not None:
        if not isinstance(existing, Doctor):
            raise RuntimeError(
                f"Username '{username}' khong phai Doctor"
            )

        return existing

    doctor = Doctor(
        username=username,
        password=hash_password(
            PASSWORDS[username]
        ),
        full_name=full_name,
        email=email,
        phone=phone,
        gender=gender,
        role=UserRole.DOCTOR,
        status=status,
        type="doctor",
        specialty_id=specialty_id,
        qualification=qualification,
        bio=bio,
    )

    db.add(doctor)
    db.flush()

    return doctor


def get_or_create_patient(
    db: Session,
    *,
    username: str,
    full_name: str,
    email: str,
    phone: str,
    gender: Gender,
    dob: date,
    address: str,
    status: UserStatus = UserStatus.ACTIVE,
) -> Patient:

    existing = get_user(
        db,
        username,
    )

    if existing is not None:
        if not isinstance(existing, Patient):
            raise RuntimeError(
                f"Username '{username}' khong phai Patient"
            )

        return existing

    patient = Patient(
        username=username,
        password=hash_password(
            PASSWORDS[username]
        ),
        full_name=full_name,
        email=email,
        phone=phone,
        gender=gender,
        role=UserRole.PATIENT,
        status=status,
        type="patient",
        dob=dob,
        address=address,
    )

    db.add(patient)
    db.flush()

    return patient


# ============================================================
# WORKING SCHEDULE
# ============================================================

def get_or_create_schedule(
    db: Session,
    *,
    doctor_id: int,
    work_date: date,
    start_time: time,
    end_time: time,
    status: WorkingScheduleStatus = WorkingScheduleStatus.ACTIVE,
) -> WorkingSchedule:

    schedule = db.execute(
        select(WorkingSchedule).where(
            WorkingSchedule.doctor_id == doctor_id,
            WorkingSchedule.work_date == work_date,
            WorkingSchedule.start_time == start_time,
            WorkingSchedule.end_time == end_time,
        )
    ).scalar_one_or_none()

    if schedule is not None:
        return schedule

    schedule = WorkingSchedule(
        doctor_id=doctor_id,
        work_date=work_date,
        start_time=start_time,
        end_time=end_time,
        status=status,
    )

    db.add(schedule)
    db.flush()

    return schedule


# ============================================================
# APPOINTMENT
# ============================================================

def get_or_create_appointment(
    db: Session,
    *,
    schedule_id: int,
    patient_id: int,
    appointment_time: datetime,
    status: AppointmentStatus,
    created_by: AppointmentCreatedBy,
    note: str | None = None,
) -> Appointment:

    appointment = db.execute(
        select(Appointment).where(
            Appointment.schedule_id == schedule_id,
            Appointment.patient_id == patient_id,
            Appointment.appointment_time == appointment_time,
        )
    ).scalar_one_or_none()

    if appointment is not None:
        return appointment

    appointment = Appointment(
        schedule_id=schedule_id,
        patient_id=patient_id,
        appointment_time=appointment_time,
        status=status,
        created_by=created_by,
        note=note,
    )

    db.add(appointment)
    db.flush()

    return appointment


# ============================================================
# MEDICAL RECORD
# ============================================================

def get_or_create_record(
    db: Session,
    *,
    appointment_id: int,
    symptoms: str,
    diagnosis: str,
    note: str | None,
    examined_at: datetime,
) -> MedicalRecord:

    record = db.execute(
        select(MedicalRecord).where(
            MedicalRecord.appointment_id == appointment_id
        )
    ).scalar_one_or_none()

    if record is not None:
        return record

    record = MedicalRecord(
        appointment_id=appointment_id,
        symptoms=symptoms,
        diagnosis=diagnosis,
        note=note,
        examined_at=examined_at,
    )

    db.add(record)
    db.flush()

    return record


# ============================================================
# PRESCRIPTION
# ============================================================

def get_or_create_prescription(
    db: Session,
    *,
    record_id: int,
    details: list[dict],
) -> tuple[Prescription, bool]:

    prescription = db.execute(
        select(Prescription).where(
            Prescription.record_id == record_id
        )
    ).scalar_one_or_none()

    if prescription is not None:
        return prescription, False

    prescription = Prescription(
        record_id=record_id
    )

    db.add(prescription)
    db.flush()

    for item in details:

        detail = PrescriptionDetail(
            prescription_id=prescription.prescription_id,
            medicine_id=item["medicine_id"],
            quantity=item["quantity"],
            dosage=item["dosage"],
            usage_note=item["usage_note"],
        )

        db.add(detail)

    db.flush()

    return prescription, True


# ============================================================
# INVOICE
# ============================================================

def calculate_medicine_total(
    details: list[dict],
) -> Decimal:

    total = Decimal("0.00")

    for item in details:
        total += (
            item["price"]
            * item["quantity"]
        )

    return total


def get_or_create_invoice(
    db: Session,
    *,
    appointment_id: int,
    total_amount: Decimal,
    status: InvoiceStatus,
    payment_method: PaymentMethod | None,
    paid_at: datetime | None,
) -> tuple[Invoice, bool]:

    invoice = db.execute(
        select(Invoice).where(
            Invoice.appointment_id == appointment_id
        )
    ).scalar_one_or_none()

    if invoice is not None:
        return invoice, False

    invoice = Invoice(
        appointment_id=appointment_id,
        total_amount=total_amount,
        status=status,
        payment_method=payment_method,
        paid_at=paid_at,
    )

    db.add(invoice)
    db.flush()

    return invoice, True


def decrease_stock(
    details: list[dict],
) -> None:

    for item in details:
        medicine = item["medicine"]

        medicine.stock_qty -= item["quantity"]


# ============================================================
# CHAT
# ============================================================

def get_or_create_chat_session(
    db: Session,
    *,
    patient_id: int,
    appointment_id: int,
) -> ChatSession:

    appointment = db.get(
        Appointment,
        appointment_id,
    )

    if appointment is None:
        raise RuntimeError(
            "Appointment khong ton tai"
        )

    if appointment.chat_session_id is not None:
        session = db.get(
            ChatSession,
            appointment.chat_session_id,
        )

        if session is not None:
            return session

    session = ChatSession(
        patient_id=patient_id
    )

    db.add(session)
    db.flush()

    appointment.chat_session_id = (
        session.session_id
    )

    db.flush()

    return session


def seed_chat_messages(
    db: Session,
    *,
    session_id: int,
    patient_content: str,
    patient_intent: str,
    ai_content: str,
    ai_intent: str,
) -> None:

    existing = db.execute(
        select(ChatMessage).where(
            ChatMessage.session_id == session_id
        )
    ).scalars().all()

    if existing:
        return

    db.add_all(
        [
            ChatMessage(
                session_id=session_id,
                sender_type=ChatSenderType.PATIENT,
                content=patient_content,
                intent=patient_intent,
            ),
            ChatMessage(
                session_id=session_id,
                sender_type=ChatSenderType.AI,
                content=ai_content,
                intent=ai_intent,
            ),
        ]
    )


# ============================================================
# RESET DATABASE
# ============================================================

def reset_seed_data(
    db: Session,
) -> None:

    print("Dang xoa du lieu cu...")

    # Child tables
    db.execute(
        delete(ChatMessage)
    )

    db.execute(
        delete(PrescriptionDetail)
    )

    db.execute(
        delete(Prescription)
    )

    db.execute(
        delete(Invoice)
    )

    db.execute(
        delete(MedicalRecord)
    )

    db.execute(
        delete(Appointment)
    )

    db.execute(
        delete(ChatSession)
    )

    db.execute(
        delete(WorkingSchedule)
    )

    # Inheritance child tables
    db.execute(
        delete(Doctor)
    )

    db.execute(
        delete(Patient)
    )

    db.execute(
        delete(Receptionist)
    )

    db.execute(
        delete(Admin)
    )

    # Parent / catalog
    db.execute(
        delete(User)
    )

    db.execute(
        delete(Medicine)
    )

    db.execute(
        delete(Specialty)
    )

    db.commit()

    print("Da xoa du lieu seed cu.")


# ============================================================
# SEED SPECIALTIES
# ============================================================

def seed_specialties(
    db: Session,
) -> dict:

    specialties = {}

    rows = [
        (
            "Tim mach",
            "Kham va dieu tri cac benh ly tim mach.",
        ),
        (
            "Nhi khoa",
            "Kham va dieu tri benh ly tre em.",
        ),
        (
            "Da lieu",
            "Kham va dieu tri cac benh ly ve da.",
        ),
        (
            "Noi tong quat",
            "Kham va dieu tri cac benh noi khoa thong thuong.",
        ),
        (
            "Tai Mui Hong",
            "Kham cac benh ly tai, mui va hong.",
        ),
        (
            "Rang Ham Mat",
            "Kham va dieu tri cac benh ly rang ham mat.",
        ),
    ]

    for name, description in rows:

        specialty, _ = get_or_create_specialty(
            db,
            name=name,
            description=description,
        )

        specialties[name] = specialty

    return specialties


# ============================================================
# SEED MEDICINES
# ============================================================

def seed_medicines(
    db: Session,
) -> dict:

    medicines = {}

    rows = [
        {
            "key": "paracetamol",
            "name": "Paracetamol 500mg",
            "unit": "Vien",
            "price": Decimal("2000.00"),
            "stock_qty": 200,
            "status": MedicineStatus.ACTIVE,
        },
        {
            "key": "amoxicillin",
            "name": "Amoxicillin 500mg",
            "unit": "Vien",
            "price": Decimal("3500.00"),
            "stock_qty": 120,
            "status": MedicineStatus.ACTIVE,
        },
        {
            "key": "vitamin_c",
            "name": "Vitamin C 500mg",
            "unit": "Vien",
            "price": Decimal("1500.00"),
            "stock_qty": 150,
            "status": MedicineStatus.ACTIVE,
        },
        {
            "key": "loratadine",
            "name": "Loratadine 10mg",
            "unit": "Vien",
            "price": Decimal("2500.00"),
            "stock_qty": 80,
            "status": MedicineStatus.ACTIVE,
        },
        {
            "key": "omeprazole",
            "name": "Omeprazole 20mg",
            "unit": "Vien",
            "price": Decimal("3000.00"),
            "stock_qty": 70,
            "status": MedicineStatus.ACTIVE,
        },
        {
            "key": "saline",
            "name": "Nuoc muoi sinh ly",
            "unit": "Chai",
            "price": Decimal("8000.00"),
            "stock_qty": 60,
            "status": MedicineStatus.ACTIVE,
        },
        {
            "key": "low_stock",
            "name": "Thuoc Test Ton Kho Thap",
            "unit": "Vien",
            "price": Decimal("5000.00"),
            "stock_qty": 3,
            "status": MedicineStatus.ACTIVE,
        },
        {
            "key": "discontinued",
            "name": "Thuoc Discontinued Test",
            "unit": "Hop",
            "price": Decimal("10000.00"),
            "stock_qty": 20,
            "status": MedicineStatus.DISCONTINUED,
        },
    ]

    for item in rows:

        medicine, _ = get_or_create_medicine(
            db,
            name=item["name"],
            unit=item["unit"],
            price=item["price"],
            stock_qty=item["stock_qty"],
            status=item["status"],
        )

        medicines[item["key"]] = medicine

    return medicines


# ============================================================
# SEED USERS
# ============================================================

def seed_users(
    db: Session,
    specialties: dict,
) -> dict:

    users = {}

    # --------------------------------------------------------
    # Admin
    # --------------------------------------------------------

    users["admin"] = get_or_create_admin(
        db,
        username="admin",
        full_name="System Administrator",
        email="admin@clinic.local",
        phone="0900000001",
        gender=Gender.MALE,
    )

    users["admin02"] = get_or_create_admin(
        db,
        username="admin02",
        full_name="Nguyen Thanh Nam",
        email="admin02@clinic.local",
        phone="0900000003",
        gender=Gender.MALE,
    )

    # --------------------------------------------------------
    # Receptionist
    # --------------------------------------------------------

    users["receptionist01"] = get_or_create_receptionist(
        db,
        username="receptionist01",
        full_name="Le Thi Thu Ha",
        email="receptionist01@clinic.local",
        phone="0900000002",
        gender=Gender.FEMALE,
    )

    users["receptionist02"] = get_or_create_receptionist(
        db,
        username="receptionist02",
        full_name="Vo Thi Mai",
        email="receptionist02@clinic.local",
        phone="0900000004",
        gender=Gender.FEMALE,
    )

    # --------------------------------------------------------
    # Doctors
    # --------------------------------------------------------

    doctor_rows = [
        (
            "doctor01",
            "Nguyen Van Minh",
            "doctor01@clinic.local",
            "0900000011",
            Gender.MALE,
            specialties["Tim mach"],
            "BS.CKII Tim mach",
            "Bac si tim mach, hon 10 nam kinh nghiem.",
            UserStatus.ACTIVE,
        ),
        (
            "doctor02",
            "Tran Thi Lan",
            "doctor02@clinic.local",
            "0900000012",
            Gender.FEMALE,
            specialties["Nhi khoa"],
            "BS.CKII Nhi khoa",
            "Bac si nhi khoa.",
            UserStatus.ACTIVE,
        ),
        (
            "doctor03",
            "Pham Quoc Huy",
            "doctor03@clinic.local",
            "0900000013",
            Gender.MALE,
            specialties["Da lieu"],
            "BS Da lieu",
            "Bac si chuyen khoa da lieu.",
            UserStatus.ACTIVE,
        ),
        (
            "doctor04",
            "Hoang Thi Mai",
            "doctor04@clinic.local",
            "0900000014",
            Gender.FEMALE,
            specialties["Noi tong quat"],
            "BS Noi tong quat",
            "Bac si noi khoa tong quat.",
            UserStatus.ACTIVE,
        ),
        (
            "doctor05",
            "Doan Minh Khang",
            "doctor05@clinic.local",
            "0900000015",
            Gender.MALE,
            specialties["Tai Mui Hong"],
            "BS.CKI Tai Mui Hong",
            "Bac si tai mui hong.",
            UserStatus.ACTIVE,
        ),
        (
            "doctor06",
            "Nguyen Thi Ngoc",
            "doctor06@clinic.local",
            "0900000016",
            Gender.FEMALE,
            specialties["Rang Ham Mat"],
            "BS Rang Ham Mat",
            "Bac si rang ham mat.",
            UserStatus.LOCKED,
        ),
    ]

    for (
        username,
        full_name,
        email,
        phone,
        gender,
        specialty,
        qualification,
        bio,
        status,
    ) in doctor_rows:

        users[username] = get_or_create_doctor(
            db,
            username=username,
            full_name=full_name,
            email=email,
            phone=phone,
            gender=gender,
            specialty_id=specialty.specialty_id,
            qualification=qualification,
            bio=bio,
            status=status,
        )

    # --------------------------------------------------------
    # Patients
    # --------------------------------------------------------

    patient_rows = [
        (
            "patient01",
            "Nguyen Van An",
            "patient01@clinic.local",
            "0911111111",
            Gender.MALE,
            date(1998, 5, 12),
            "Quan 1, TP.HCM",
            UserStatus.ACTIVE,
        ),
        (
            "patient02",
            "Le Thi Bich",
            "patient02@clinic.local",
            "0911111112",
            Gender.FEMALE,
            date(1995, 8, 20),
            "Quan 3, TP.HCM",
            UserStatus.ACTIVE,
        ),
        (
            "patient03",
            "Pham Van Cuong",
            "patient03@clinic.local",
            "0911111113",
            Gender.MALE,
            date(2000, 2, 10),
            "Thu Duc, TP.HCM",
            UserStatus.ACTIVE,
        ),
        (
            "patient04",
            "Tran Minh Chau",
            "patient04@clinic.local",
            "0911111114",
            Gender.FEMALE,
            date(2002, 3, 18),
            "Quan 7, TP.HCM",
            UserStatus.ACTIVE,
        ),
        (
            "patient05",
            "Vo Hoang Long",
            "patient05@clinic.local",
            "0911111115",
            Gender.MALE,
            date(1994, 11, 2),
            "Binh Thanh, TP.HCM",
            UserStatus.ACTIVE,
        ),
        (
            "patient06",
            "Nguyen Thi Hoa",
            "patient06@clinic.local",
            "0911111116",
            Gender.FEMALE,
            date(1990, 7, 25),
            "Go Vap, TP.HCM",
            UserStatus.ACTIVE,
        ),
        (
            "patient07",
            "Do Duc Anh",
            "patient07@clinic.local",
            "0911111117",
            Gender.MALE,
            date(1999, 9, 9),
            "Tan Binh, TP.HCM",
            UserStatus.ACTIVE,
        ),
        (
            "patient08",
            "Bui Ngoc Anh",
            "patient08@clinic.local",
            "0911111118",
            Gender.FEMALE,
            date(2001, 1, 27),
            "Phu Nhuan, TP.HCM",
            UserStatus.ACTIVE,
        ),
        (
            "patient09",
            "Pham Gia Bao",
            "patient09@clinic.local",
            "0911111119",
            Gender.MALE,
            date(1988, 6, 13),
            "Quan 10, TP.HCM",
            UserStatus.ACTIVE,
        ),
        (
            "patient10",
            "Huynh Kim Ngan",
            "patient10@clinic.local",
            "0911111120",
            Gender.FEMALE,
            date(1997, 12, 4),
            "Quan 5, TP.HCM",
            UserStatus.ACTIVE,
        ),
        (
            "patient11",
            "Mai Thanh Tung",
            "patient11@clinic.local",
            "0911111121",
            Gender.MALE,
            date(1992, 10, 15),
            "Binh Tan, TP.HCM",
            UserStatus.ACTIVE,
        ),
        (
            "patient12",
            "Ngo Thi Yen",
            "patient12@clinic.local",
            "0911111122",
            Gender.FEMALE,
            date(1996, 4, 30),
            "Quan 11, TP.HCM",
            UserStatus.LOCKED,
        ),
    ]

    for (
        username,
        full_name,
        email,
        phone,
        gender,
        dob,
        address,
        status,
    ) in patient_rows:

        users[username] = get_or_create_patient(
            db,
            username=username,
            full_name=full_name,
            email=email,
            phone=phone,
            gender=gender,
            dob=dob,
            address=address,
            status=status,
        )

    return users


# ============================================================
# SEED SCHEDULES
# ============================================================

def seed_schedules(
    db: Session,
    users: dict,
) -> dict:

    today = date.today()
    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)

    day_7 = today - timedelta(days=7)
    day_30 = today - timedelta(days=30)
    day_60 = today - timedelta(days=60)

    tomorrow = today + timedelta(days=1)
    day_2 = today + timedelta(days=2)
    day_7_future = today + timedelta(days=7)

    d1 = users["doctor01"].user_id
    d2 = users["doctor02"].user_id
    d3 = users["doctor03"].user_id
    d4 = users["doctor04"].user_id
    d5 = users["doctor05"].user_id
    d6 = users["doctor06"].user_id

    schedules = {}

    # --------------------------------------------------------
    # Doctor 1 - Tim mach
    # --------------------------------------------------------

    schedules["d1_today"] = get_or_create_schedule(
        db,
        doctor_id=d1,
        work_date=today,
        start_time=time(8, 0),
        end_time=time(12, 0),
    )

    schedules["d1_yesterday"] = get_or_create_schedule(
        db,
        doctor_id=d1,
        work_date=yesterday,
        start_time=time(8, 0),
        end_time=time(12, 0),
    )

    schedules["d1_30days"] = get_or_create_schedule(
        db,
        doctor_id=d1,
        work_date=day_30,
        start_time=time(8, 0),
        end_time=time(11, 0),
    )

    schedules["d1_tomorrow"] = get_or_create_schedule(
        db,
        doctor_id=d1,
        work_date=tomorrow,
        start_time=time(8, 0),
        end_time=time(12, 0),
    )

    # --------------------------------------------------------
    # Doctor 2 - Nhi khoa
    # --------------------------------------------------------

    schedules["d2_today"] = get_or_create_schedule(
        db,
        doctor_id=d2,
        work_date=today,
        start_time=time(13, 0),
        end_time=time(17, 0),
    )

    schedules["d2_7days"] = get_or_create_schedule(
        db,
        doctor_id=d2,
        work_date=day_7,
        start_time=time(13, 0),
        end_time=time(17, 0),
    )

    schedules["d2_tomorrow"] = get_or_create_schedule(
        db,
        doctor_id=d2,
        work_date=tomorrow,
        start_time=time(13, 0),
        end_time=time(17, 0),
    )

    # --------------------------------------------------------
    # Doctor 3 - Da lieu
    # --------------------------------------------------------

    schedules["d3_today"] = get_or_create_schedule(
        db,
        doctor_id=d3,
        work_date=today,
        start_time=time(15, 0),
        end_time=time(18, 0),
    )

    schedules["d3_60days"] = get_or_create_schedule(
        db,
        doctor_id=d3,
        work_date=day_60,
        start_time=time(14, 0),
        end_time=time(17, 0),
    )

    schedules["d3_day2"] = get_or_create_schedule(
        db,
        doctor_id=d3,
        work_date=day_2,
        start_time=time(15, 0),
        end_time=time(18, 0),
    )

    # --------------------------------------------------------
    # Doctor 4 - Noi tong quat
    # --------------------------------------------------------

    schedules["d4_yesterday"] = get_or_create_schedule(
        db,
        doctor_id=d4,
        work_date=yesterday,
        start_time=time(8, 0),
        end_time=time(11, 0),
    )

    schedules["d4_day7future"] = get_or_create_schedule(
        db,
        doctor_id=d4,
        work_date=day_7_future,
        start_time=time(8, 0),
        end_time=time(12, 0),
    )

    # --------------------------------------------------------
    # Doctor 5 - Tai Mui Hong
    # --------------------------------------------------------

    schedules["d5_two_days"] = get_or_create_schedule(
        db,
        doctor_id=d5,
        work_date=two_days_ago,
        start_time=time(13, 0),
        end_time=time(17, 0),
    )

    schedules["d5_day2"] = get_or_create_schedule(
        db,
        doctor_id=d5,
        work_date=day_2,
        start_time=time(13, 0),
        end_time=time(17, 0),
    )

    # --------------------------------------------------------
    # Doctor 6 - Locked
    # --------------------------------------------------------

    schedules["d6_off"] = get_or_create_schedule(
        db,
        doctor_id=d6,
        work_date=day_7_future,
        start_time=time(14, 0),
        end_time=time(17, 0),
        status=WorkingScheduleStatus.OFF,
    )

    return schedules


# ============================================================
# SEED APPOINTMENTS
# ============================================================

def seed_appointments(
    db: Session,
    users: dict,
    schedules: dict,
) -> dict:

    p1 = users["patient01"].user_id
    p2 = users["patient02"].user_id
    p3 = users["patient03"].user_id
    p4 = users["patient04"].user_id
    p5 = users["patient05"].user_id
    p6 = users["patient06"].user_id
    p7 = users["patient07"].user_id
    p8 = users["patient08"].user_id
    p9 = users["patient09"].user_id
    p10 = users["patient10"].user_id
    p11 = users["patient11"].user_id

    today = date.today()
    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)

    day_7 = today - timedelta(days=7)
    day_30 = today - timedelta(days=30)
    day_60 = today - timedelta(days=60)

    tomorrow = today + timedelta(days=1)
    day_2 = today + timedelta(days=2)
    day_7_future = today + timedelta(days=7)

    appointments = {}

    # ========================================================
    # TODAY
    # ========================================================

    appointments["today_completed_1"] = get_or_create_appointment(
        db,
        schedule_id=schedules["d1_today"].schedule_id,
        patient_id=p1,
        appointment_time=datetime.combine(
            today,
            time(8, 30),
        ),
        status=AppointmentStatus.COMPLETED,
        created_by=AppointmentCreatedBy.PATIENT,
        note="Tai kham tim mach.",
    )

    appointments["today_completed_2"] = get_or_create_appointment(
        db,
        schedule_id=schedules["d1_today"].schedule_id,
        patient_id=p2,
        appointment_time=datetime.combine(
            today,
            time(9, 0),
        ),
        status=AppointmentStatus.COMPLETED,
        created_by=AppointmentCreatedBy.RECEPTIONIST,
        note="Kham dinh ky.",
    )

    appointments["today_pending"] = get_or_create_appointment(
        db,
        schedule_id=schedules["d2_today"].schedule_id,
        patient_id=p3,
        appointment_time=datetime.combine(
            today,
            time(11, 0),
        ),
        status=AppointmentStatus.PENDING,
        created_by=AppointmentCreatedBy.PATIENT,
        note="Cho tiep nhan.",
    )

    appointments["today_confirmed_1"] = get_or_create_appointment(
        db,
        schedule_id=schedules["d2_today"].schedule_id,
        patient_id=p4,
        appointment_time=datetime.combine(
            today,
            time(13, 30),
        ),
        status=AppointmentStatus.CONFIRMED,
        created_by=AppointmentCreatedBy.RECEPTIONIST,
        note="Da tiep nhan, dang cho bac si.",
    )

    appointments["today_confirmed_2"] = get_or_create_appointment(
        db,
        schedule_id=schedules["d3_today"].schedule_id,
        patient_id=p5,
        appointment_time=datetime.combine(
            today,
            time(15, 30),
        ),
        status=AppointmentStatus.CONFIRMED,
        created_by=AppointmentCreatedBy.PATIENT,
        note="Cho kham da lieu.",
    )

    # ========================================================
    # YESTERDAY
    # ========================================================

    appointments["yesterday_completed_1"] = get_or_create_appointment(
        db,
        schedule_id=schedules["d1_yesterday"].schedule_id,
        patient_id=p6,
        appointment_time=datetime.combine(
            yesterday,
            time(8, 30),
        ),
        status=AppointmentStatus.COMPLETED,
        created_by=AppointmentCreatedBy.RECEPTIONIST,
        note="Tai kham dau dau.",
    )

    appointments["yesterday_cancelled"] = get_or_create_appointment(
        db,
        schedule_id=schedules["d1_yesterday"].schedule_id,
        patient_id=p7,
        appointment_time=datetime.combine(
            yesterday,
            time(9, 30),
        ),
        status=AppointmentStatus.CANCELLED,
        created_by=AppointmentCreatedBy.PATIENT,
        note="Benh nhan huy lich.",
    )

    # ========================================================
    # 7 DAYS AGO
    # ========================================================

    appointments["day7_completed"] = get_or_create_appointment(
        db,
        schedule_id=schedules["d2_7days"].schedule_id,
        patient_id=p8,
        appointment_time=datetime.combine(
            day_7,
            time(14, 0),
        ),
        status=AppointmentStatus.COMPLETED,
        created_by=AppointmentCreatedBy.RECEPTIONIST,
        note="Kham nhi.",
    )

    # ========================================================
    # 30 DAYS AGO
    # ========================================================

    appointments["day30_completed"] = get_or_create_appointment(
        db,
        schedule_id=schedules["d1_30days"].schedule_id,
        patient_id=p9,
        appointment_time=datetime.combine(
            day_30,
            time(8, 30),
        ),
        status=AppointmentStatus.COMPLETED,
        created_by=AppointmentCreatedBy.PATIENT,
        note="Kham tim mach.",
    )

    appointments["day30_completed_2"] = get_or_create_appointment(
        db,
        schedule_id=schedules["d1_30days"].schedule_id,
        patient_id=p10,
        appointment_time=datetime.combine(
            day_30,
            time(9, 0),
        ),
        status=AppointmentStatus.COMPLETED,
        created_by=AppointmentCreatedBy.RECEPTIONIST,
        note="Tai kham tim mach.",
    )

    # ========================================================
    # 60 DAYS AGO
    # ========================================================

    appointments["day60_completed"] = get_or_create_appointment(
        db,
        schedule_id=schedules["d3_60days"].schedule_id,
        patient_id=p11,
        appointment_time=datetime.combine(
            day_60,
            time(14, 30),
        ),
        status=AppointmentStatus.COMPLETED,
        created_by=AppointmentCreatedBy.AI,
        note="Appointment duoc tao boi AI Assistant.",
    )

    # ========================================================
    # 2 DAYS AGO
    # ========================================================

    appointments["two_days_completed"] = get_or_create_appointment(
        db,
        schedule_id=schedules["d5_two_days"].schedule_id,
        patient_id=p1,
        appointment_time=datetime.combine(
            two_days_ago,
            time(13, 30),
        ),
        status=AppointmentStatus.COMPLETED,
        created_by=AppointmentCreatedBy.AI,
        note="Tao boi AI Assistant.",
    )

    # ========================================================
    # TOMORROW
    # ========================================================

    appointments["tomorrow_pending"] = get_or_create_appointment(
        db,
        schedule_id=schedules["d1_tomorrow"].schedule_id,
        patient_id=p2,
        appointment_time=datetime.combine(
            tomorrow,
            time(8, 0),
        ),
        status=AppointmentStatus.PENDING,
        created_by=AppointmentCreatedBy.PATIENT,
        note="Lich cho tiep nhan ngay mai.",
    )

    appointments["tomorrow_confirmed"] = get_or_create_appointment(
        db,
        schedule_id=schedules["d1_tomorrow"].schedule_id,
        patient_id=p3,
        appointment_time=datetime.combine(
            tomorrow,
            time(8, 30),
        ),
        status=AppointmentStatus.CONFIRMED,
        created_by=AppointmentCreatedBy.RECEPTIONIST,
        note="Da xac nhan cho ngay mai.",
    )

    appointments["tomorrow_cancelled"] = get_or_create_appointment(
        db,
        schedule_id=schedules["d2_tomorrow"].schedule_id,
        patient_id=p4,
        appointment_time=datetime.combine(
            tomorrow,
            time(14, 0),
        ),
        status=AppointmentStatus.CANCELLED,
        created_by=AppointmentCreatedBy.RECEPTIONIST,
        note="Test Cancelled.",
    )

    # ========================================================
    # DAY 2 FUTURE
    # ========================================================

    appointments["day2_pending"] = get_or_create_appointment(
        db,
        schedule_id=schedules["d3_day2"].schedule_id,
        patient_id=p5,
        appointment_time=datetime.combine(
            day_2,
            time(15, 0),
        ),
        status=AppointmentStatus.PENDING,
        created_by=AppointmentCreatedBy.AI,
        note="AI ho tro dat lich.",
    )

    appointments["day2_confirmed"] = get_or_create_appointment(
        db,
        schedule_id=schedules["d5_day2"].schedule_id,
        patient_id=p6,
        appointment_time=datetime.combine(
            day_2,
            time(13, 30),
        ),
        status=AppointmentStatus.CONFIRMED,
        created_by=AppointmentCreatedBy.PATIENT,
        note="Lich da xac nhan.",
    )

    # ========================================================
    # 7 DAYS FUTURE
    # ========================================================

    appointments["day7future_confirmed"] = get_or_create_appointment(
        db,
        schedule_id=schedules["d4_day7future"].schedule_id,
        patient_id=p7,
        appointment_time=datetime.combine(
            day_7_future,
            time(8, 0),
        ),
        status=AppointmentStatus.CONFIRMED,
        created_by=AppointmentCreatedBy.PATIENT,
        note="Lich kham tuong lai.",
    )

    return appointments


# ============================================================
# MEDICAL RECORDS + PRESCRIPTIONS + INVOICES
# ============================================================

def seed_records_prescriptions_invoices(
    db: Session,
    users: dict,
    medicines: dict,
    appointments: dict,
) -> None:

    now = datetime.now()

    p = medicines

    # ========================================================
    # 1. Today completed - Patient 1
    # ========================================================

    appt = appointments["today_completed_1"]

    record = get_or_create_record(
        db,
        appointment_id=appt.appointment_id,
        symptoms="Dau dau nhe, met moi, choang vang.",
        diagnosis="Thieu ngu va cang thang.",
        note="Theo doi them 1 tuan.",
        examined_at=appt.appointment_time + timedelta(
            minutes=20
        ),
    )

    prescription_details = [
        {
            "medicine": p["paracetamol"],
            "medicine_id": p["paracetamol"].medicine_id,
            "price": p["paracetamol"].price,
            "quantity": 2,
            "dosage": "1 vien moi lan, ngay 2 lan",
            "usage_note": "Uong sau an.",
        },
        {
            "medicine": p["vitamin_c"],
            "medicine_id": p["vitamin_c"].medicine_id,
            "price": p["vitamin_c"].price,
            "quantity": 2,
            "dosage": "1 vien moi ngay",
            "usage_note": "Uong sau an sang.",
        },
    ]

    _, created = get_or_create_prescription(
        db,
        record_id=record.record_id,
        details=prescription_details,
    )

    invoice_total = (
        CONSULTATION_FEE
        + calculate_medicine_total(
            prescription_details
        )
    )

    invoice, invoice_created = get_or_create_invoice(
        db,
        appointment_id=appt.appointment_id,
        total_amount=invoice_total,
        status=InvoiceStatus.PAID,
        payment_method=PaymentMethod.CASH,
        paid_at=now,
    )

    if created and invoice_created:
        decrease_stock(
            prescription_details
        )

    # ========================================================
    # 2. Today completed - Patient 2
    # ========================================================

    appt = appointments["today_completed_2"]

    record = get_or_create_record(
        db,
        appointment_id=appt.appointment_id,
        symptoms="Ho, dau hong, so mui.",
        diagnosis="Viem hong cap.",
        note="Uong du nuoc, nghi ngoi.",
        examined_at=appt.appointment_time + timedelta(
            minutes=20
        ),
    )

    prescription_details = [
        {
            "medicine": p["amoxicillin"],
            "medicine_id": p["amoxicillin"].medicine_id,
            "price": p["amoxicillin"].price,
            "quantity": 5,
            "dosage": "1 vien moi ngay",
            "usage_note": "Uong sau an.",
        },
        {
            "medicine": p["vitamin_c"],
            "medicine_id": p["vitamin_c"].medicine_id,
            "price": p["vitamin_c"].price,
            "quantity": 2,
            "dosage": "1 vien moi ngay",
            "usage_note": "Uong sau an.",
        },
    ]

    _, created = get_or_create_prescription(
        db,
        record_id=record.record_id,
        details=prescription_details,
    )

    invoice_total = (
        CONSULTATION_FEE
        + calculate_medicine_total(
            prescription_details
        )
    )

    _, invoice_created = get_or_create_invoice(
        db,
        appointment_id=appt.appointment_id,
        total_amount=invoice_total,
        status=InvoiceStatus.PAID,
        payment_method=PaymentMethod.ONLINE,
        paid_at=now,
    )

    if created and invoice_created:
        decrease_stock(
            prescription_details
        )

    # ========================================================
    # 3. Yesterday completed
    # ========================================================

    appt = appointments["yesterday_completed_1"]

    record = get_or_create_record(
        db,
        appointment_id=appt.appointment_id,
        symptoms="Dau bung nhe sau khi an.",
        diagnosis="Roi loan tieu hoa.",
        note="Dieu chinh che do an.",
        examined_at=appt.appointment_time + timedelta(
            minutes=20
        ),
    )

    prescription_details = [
        {
            "medicine": p["omeprazole"],
            "medicine_id": p["omeprazole"].medicine_id,
            "price": p["omeprazole"].price,
            "quantity": 5,
            "dosage": "1 vien moi ngay",
            "usage_note": "Uong truoc bua sang.",
        }
    ]

    _, created = get_or_create_prescription(
        db,
        record_id=record.record_id,
        details=prescription_details,
    )

    invoice_total = (
        CONSULTATION_FEE
        + calculate_medicine_total(
            prescription_details
        )
    )

    _, invoice_created = get_or_create_invoice(
        db,
        appointment_id=appt.appointment_id,
        total_amount=invoice_total,
        status=InvoiceStatus.PAID,
        payment_method=PaymentMethod.CASH,
        paid_at=now - timedelta(days=1),
    )

    if created and invoice_created:
        decrease_stock(
            prescription_details
        )

    # ========================================================
    # 4. 7 days completed - No prescription
    # ========================================================

    appt = appointments["day7_completed"]

    record = get_or_create_record(
        db,
        appointment_id=appt.appointment_id,
        symptoms="Kham suc khoe tre em.",
        diagnosis="Suc khoe on dinh.",
        note="Tiep tuc theo doi.",
        examined_at=appt.appointment_time + timedelta(
            minutes=15
        ),
    )

    get_or_create_invoice(
        db,
        appointment_id=appt.appointment_id,
        total_amount=CONSULTATION_FEE,
        status=InvoiceStatus.PAID,
        payment_method=PaymentMethod.ONLINE,
        paid_at=now - timedelta(days=7),
    )

    # ========================================================
    # 5. 30 days completed - UNPAID
    # ========================================================

    appt = appointments["day30_completed"]

    record = get_or_create_record(
        db,
        appointment_id=appt.appointment_id,
        symptoms="Dau dau, hoa mat.",
        diagnosis="Thieu ngu va cang thang.",
        note="Can ngu du giac.",
        examined_at=appt.appointment_time + timedelta(
            minutes=20
        ),
    )

    prescription_details = [
        {
            "medicine": p["paracetamol"],
            "medicine_id": p["paracetamol"].medicine_id,
            "price": p["paracetamol"].price,
            "quantity": 3,
            "dosage": "1 vien khi dau",
            "usage_note": "Khong qua 3 vien/ngay.",
        },
        {
            "medicine": p["vitamin_c"],
            "medicine_id": p["vitamin_c"].medicine_id,
            "price": p["vitamin_c"].price,
            "quantity": 2,
            "dosage": "1 vien moi ngay",
            "usage_note": "Uong sau an.",
        },
    ]

    get_or_create_prescription(
        db,
        record_id=record.record_id,
        details=prescription_details,
    )

    invoice_total = (
        CONSULTATION_FEE
        + calculate_medicine_total(
            prescription_details
        )
    )

    # Unpaid -> KHONG tru kho
    get_or_create_invoice(
        db,
        appointment_id=appt.appointment_id,
        total_amount=invoice_total,
        status=InvoiceStatus.UNPAID,
        payment_method=None,
        paid_at=None,
    )

    # ========================================================
    # 6. 30 days completed - PAID
    # ========================================================

    appt = appointments["day30_completed_2"]

    record = get_or_create_record(
        db,
        appointment_id=appt.appointment_id,
        symptoms="Dau nguoi, met moi.",
        diagnosis="Cam lanh thong thuong.",
        note="Nghi ngoi nhieu hon.",
        examined_at=appt.appointment_time + timedelta(
            minutes=20
        ),
    )

    prescription_details = [
        {
            "medicine": p["loratadine"],
            "medicine_id": p["loratadine"].medicine_id,
            "price": p["loratadine"].price,
            "quantity": 5,
            "dosage": "1 vien moi ngay",
            "usage_note": "Uong vao buoi toi.",
        }
    ]

    _, created = get_or_create_prescription(
        db,
        record_id=record.record_id,
        details=prescription_details,
    )

    invoice_total = (
        CONSULTATION_FEE
        + calculate_medicine_total(
            prescription_details
        )
    )

    _, invoice_created = get_or_create_invoice(
        db,
        appointment_id=appt.appointment_id,
        total_amount=invoice_total,
        status=InvoiceStatus.PAID,
        payment_method=PaymentMethod.CASH,
        paid_at=now - timedelta(days=30),
    )

    if created and invoice_created:
        decrease_stock(
            prescription_details
        )

    # ========================================================
    # 7. 60 days completed - no prescription
    # ========================================================

    appt = appointments["day60_completed"]

    get_or_create_record(
        db,
        appointment_id=appt.appointment_id,
        symptoms="Kham da.",
        diagnosis="Viem da tiep xuc nhe.",
        note="Tranh chat kich ung.",
        examined_at=appt.appointment_time + timedelta(
            minutes=20
        ),
    )

    get_or_create_invoice(
        db,
        appointment_id=appt.appointment_id,
        total_amount=CONSULTATION_FEE,
        status=InvoiceStatus.CANCELLED,
        payment_method=None,
        paid_at=None,
    )

    # ========================================================
    # 8. Two days ago - AI appointment
    # ========================================================

    appt = appointments["two_days_completed"]

    record = get_or_create_record(
        db,
        appointment_id=appt.appointment_id,
        symptoms="Nghet mui, dau dau.",
        diagnosis="Viem mui thong thuong.",
        note="Theo doi them.",
        examined_at=appt.appointment_time + timedelta(
            minutes=20
        ),
    )

    prescription_details = [
        {
            "medicine": p["saline"],
            "medicine_id": p["saline"].medicine_id,
            "price": p["saline"].price,
            "quantity": 2,
            "dosage": "Su dung 2 lan/ngay",
            "usage_note": "Rua mui.",
        }
    ]

    _, created = get_or_create_prescription(
        db,
        record_id=record.record_id,
        details=prescription_details,
    )

    invoice_total = (
        CONSULTATION_FEE
        + calculate_medicine_total(
            prescription_details
        )
    )

    _, invoice_created = get_or_create_invoice(
        db,
        appointment_id=appt.appointment_id,
        total_amount=invoice_total,
        status=InvoiceStatus.PAID,
        payment_method=PaymentMethod.ONLINE,
        paid_at=now - timedelta(days=2),
    )

    if created and invoice_created:
        decrease_stock(
            prescription_details
        )


# ============================================================
# SEED CHAT
# ============================================================

def seed_chats(
    db: Session,
    users: dict,
    appointments: dict,
) -> None:

    # AI booking
    appt = appointments["day2_pending"]

    session = get_or_create_chat_session(
        db,
        patient_id=users["patient05"].user_id,
        appointment_id=appt.appointment_id,
    )

    seed_chat_messages(
        db,
        session_id=session.session_id,
        patient_content=(
            "Toi muon dat lich voi bac si da lieu "
            "vao ngay mai."
        ),
        patient_intent="book_appointment",
        ai_content=(
            "Toi co the ho tro tim bac si va khung gio "
            "phu hop cho ban."
        ),
        ai_intent="book_appointment",
    )

    # AI appointment completed
    appt = appointments["two_days_completed"]

    session = get_or_create_chat_session(
        db,
        patient_id=users["patient01"].user_id,
        appointment_id=appt.appointment_id,
    )

    seed_chat_messages(
        db,
        session_id=session.session_id,
        patient_content=(
            "Toi muon dat lich voi bac si "
            "tai mui hong."
        ),
        patient_intent="book_appointment",
        ai_content=(
            "Da tim thay lich phu hop va ho tro ban."
        ),
        ai_intent="book_appointment",
    )


# ============================================================
# SUMMARY
# ============================================================

def print_summary(
    db: Session,
) -> None:

    print()
    print("=" * 60)
    print("SEED COMPLETED")
    print("=" * 60)

    tables = [
        ("Users", User),
        ("Admins", Admin),
        ("Receptionists", Receptionist),
        ("Doctors", Doctor),
        ("Patients", Patient),
        ("Specialties", Specialty),
        ("Medicines", Medicine),
        ("Schedules", WorkingSchedule),
        ("Appointments", Appointment),
        ("Medical Records", MedicalRecord),
        ("Prescriptions", Prescription),
        ("Prescription Details", PrescriptionDetail),
        ("Invoices", Invoice),
        ("Chat Sessions", ChatSession),
        ("Chat Messages", ChatMessage),
    ]

    for label, model in tables:

        count = db.execute(
            select(model)
        ).scalars().all()

        print(
            f"{label:<25}: {len(count)}"
        )

    print()
    print("TEST ACCOUNTS")
    print("-" * 60)

    print("Admin:")
    print("  admin / Admin123")
    print("  admin02 / Admin123")

    print()
    print("Receptionist:")
    print("  receptionist01 / Reception123")
    print("  receptionist02 / Reception123")

    print()
    print("Doctor:")
    print("  doctor01 / Doctor123")
    print("  doctor02 / Doctor123")
    print("  doctor03 / Doctor123")
    print("  doctor04 / Doctor123")
    print("  doctor05 / Doctor123")
    print("  doctor06 / Doctor123  <-- LOCKED")

    print()
    print("Patient:")
    print("  patient01 / Patient123")
    print("  patient02 / Patient123")
    print("  patient03 / Patient123")
    print("  patient04 / Patient123")
    print("  patient05 / Patient123")
    print("  patient06 / Patient123")
    print("  patient07 / Patient123")
    print("  patient08 / Patient123")
    print("  patient09 / Patient123")
    print("  patient10 / Patient123")
    print("  patient11 / Patient123")
    print("  patient12 / Patient123  <-- LOCKED")

    print()
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Seed du lieu cho Clinic Management System"
        )
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Xoa du lieu cu truoc khi seed",
    )

    args = parser.parse_args()

    db = SessionLocal()

    try:

        print("=" * 60)
        print("CLINIC MANAGEMENT SYSTEM - SEED")
        print("=" * 60)

        if args.reset:
            reset_seed_data(db)

        specialties = seed_specialties(db)

        medicines = seed_medicines(db)

        users = seed_users(
            db,
            specialties,
        )

        schedules = seed_schedules(
            db,
            users,
        )

        appointments = seed_appointments(
            db,
            users,
            schedules,
        )

        seed_records_prescriptions_invoices(
            db,
            users,
            medicines,
            appointments,
        )

        seed_chats(
            db,
            users,
            appointments,
        )

        db.commit()

        print_summary(db)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()