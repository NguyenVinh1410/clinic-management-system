from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import select
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

PASSWORDS = {
    "admin": "Admin123",
    "receptionist": "Reception123",
    "doctor01": "Doctor123",
    "doctor02": "Doctor123",
    "doctor03": "Doctor123",
    "patient01": "Patient123",
    "patient02": "Patient123",
    "patient03": "Patient123",
}

def get_user(
        db: Session,
        username: str,
) -> User | None:
    return db.execute(
        select(User)
        .where(User.username == username)
    ).scalar_one_or_none()

def get_or_create_specialty(
        db: Session,
        *,
        name: str,
        description: str,
) -> Specialty:
    specialty = db.execute(
        select(Specialty)
        .where(Specialty.name == name)
    ).scalar_one_or_none()

    if specialty is not None:
        return specialty

    specialty = Specialty(name=name, description=description)

    db.add(specialty)
    db.flush()

    return specialty

def get_or_create_medicine(
        db: Session,
        *,
        name: str,
        unit: str,
        price: Decimal,
        stock_qty: int,
        status: MedicineStatus = MedicineStatus.ACTIVE,
) -> Medicine:

    medicine = db.execute(
        select(Medicine)
        .where(Medicine.name == name)
    ).scalar_one_or_none()

    if medicine is not None:
        return medicine

    medicine = Medicine(
        name=name,
        unit=unit,
        price=price,
        stock_qty=stock_qty,
        status=status,
    )

    db.add(medicine)
    db.flush()

    return medicine

def get_or_create_admin(db: Session) -> Admin:

    existing = get_user(db, "admin")

    if existing is not None:
        if not isinstance(existing, Admin):
            raise RuntimeError("Username 'admin' dang duoc dung cho user khong phai admin")

        return existing

    admin = Admin(
        username="admin",
        password=hash_password(PASSWORDS["admin"]),
        full_name="System Administrator",
        email="admin@clinic.local",
        phone="0900000001",
        gender=Gender.MALE,
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        type="admin"
    )

    db.add(admin)
    db.flush()

    return admin

def get_or_create_receptionist(db: Session) -> Receptionist:

    existing = get_user(db, "receptionist01")

    if existing is not None:

        if not isinstance(existing, Receptionist):
            raise RuntimeError(
                "Username 'receptionist01' khong phai Receptionist"
            )

        return existing

    receptionist = Receptionist(
        username="receptionist01",
        password=hash_password(PASSWORDS["receptionist"]),
        full_name="Le Thi Thu Ha",
        email="receptionist@clinic.local",
        phone="0900000002",
        gender=Gender.FEMALE,
        role=UserRole.RECEPTIONIST,
        status=UserStatus.ACTIVE,
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
) -> Doctor:

    existing = get_user(db, username)

    if existing is not None:

        if not isinstance(existing, Doctor):
            raise RuntimeError(
                f"Username '{username}' khong phai Doctor"
            )

        return existing

    doctor = Doctor(
        username=username,
        password=hash_password(PASSWORDS[username]),
        full_name=full_name,
        email=email,
        phone=phone,
        gender=gender,
        role=UserRole.DOCTOR,
        status=UserStatus.ACTIVE,
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
) -> Patient:

    existing = get_user(db, username)

    if existing is not None:

        if not isinstance(existing, Patient):
            raise RuntimeError(
                f"Username '{username}' khong phai Patient"
            )

        return existing

    patient = Patient(
        username=username,
        password=hash_password(PASSWORDS[username]),
        full_name=full_name,
        email=email,
        phone=phone,
        gender=gender,
        role=UserRole.PATIENT,
        status=UserStatus.ACTIVE,
        type="patient",
        dob=dob,
        address=address,
    )

    db.add(patient)
    db.flush()

    return patient

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


def get_or_create_appointment(
    db: Session,
    *,
    schedule_id: int,
    patient_id: int,
    appointment_time: datetime,
    status: AppointmentStatus,
    created_by: AppointmentCreatedBy,
    note: str | None,
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


def get_or_create_prescription(
    db: Session,
    *,
    record_id: int,
    details: list[dict],
) -> Prescription:

    prescription = db.execute(
        select(Prescription).where(
            Prescription.record_id == record_id
        )
    ).scalar_one_or_none()

    if prescription is not None:
        return prescription

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

    return prescription


def get_or_create_invoice(
    db: Session,
    *,
    appointment_id: int,
    total_amount: Decimal,
    status: InvoiceStatus,
    payment_method: PaymentMethod | None,
    paid_at: datetime | None,
) -> Invoice:

    invoice = db.execute(
        select(Invoice).where(
            Invoice.appointment_id == appointment_id
        )
    ).scalar_one_or_none()

    if invoice is not None:
        return invoice

    invoice = Invoice(
        appointment_id=appointment_id,
        total_amount=total_amount,
        status=status,
        payment_method=payment_method,
        paid_at=paid_at,
    )

    db.add(invoice)
    db.flush()

    return invoice


def get_or_create_chat_session(
    db: Session,
    *,
    patient_id: int,
    appointment_id: int,
) -> ChatSession:

    session = (
        db.execute(
            select(ChatSession)
            .where(ChatSession.patient_id == patient_id)
            .order_by(ChatSession.session_id)
        )
        .scalars()
        .first()
    )

    if session is None:

        session = ChatSession(
            patient_id=patient_id
        )

        db.add(session)
        db.flush()

    appointment = db.get(
        Appointment,
        appointment_id
    )

    if (
        appointment is not None
        and appointment.chat_session_id is None
    ):
        appointment.chat_session_id = session.session_id
        db.flush()

    return session

def seed_users_and_catalog(db: Session) -> dict:

    cardio = get_or_create_specialty(
        db,
        name="Tim mach",
        description="Kham va dieu tri cac benh ly tim mach.",
    )

    pediatrics = get_or_create_specialty(
        db,
        name="Nhi khoa",
        description="Kham va dieu tri benh ly tre em.",
    )

    dermatology = get_or_create_specialty(
        db,
        name="Da lieu",
        description="Kham va dieu tri cac benh ly ve da.",
    )

    admin = get_or_create_admin(db)
    receptionist = get_or_create_receptionist(db)

    doctor01 = get_or_create_doctor(
        db,
        username="doctor01",
        full_name="Nguyen Van Minh",
        email="doctor01@clinic.local",
        phone="0900000011",
        gender=Gender.MALE,
        specialty_id=cardio.specialty_id,
        qualification="BS.CKII Tim mach",
        bio="Bac si tim mach, hon 10 nam kinh nghiem.",
    )

    doctor02 = get_or_create_doctor(
        db,
        username="doctor02",
        full_name="Tran Thi Lan",
        email="doctor02@clinic.local",
        phone="0900000012",
        gender=Gender.FEMALE,
        specialty_id=pediatrics.specialty_id,
        qualification="BS.CKII Nhi khoa",
        bio="Bac si nhi khoa.",
    )

    doctor03 = get_or_create_doctor(
        db,
        username="doctor03",
        full_name="Pham Quoc Huy",
        email="doctor03@clinic.local",
        phone="0900000013",
        gender=Gender.MALE,
        specialty_id=dermatology.specialty_id,
        qualification="BS Da lieu",
        bio="Bac si chuyen khoa da lieu.",
    )

    patient01 = get_or_create_patient(
        db,
        username="patient01",
        full_name="Nguyen Van A",
        email="patient01@clinic.local",
        phone="0911111111",
        gender=Gender.MALE,
        dob=date(1998, 5, 12),
        address="Quan 1, TP.HCM",
    )

    patient02 = get_or_create_patient(
        db,
        username="patient02",
        full_name="Le Thi B",
        email="patient02@clinic.local",
        phone="0911111112",
        gender=Gender.FEMALE,
        dob=date(1995, 8, 20),
        address="Quan 3, TP.HCM",
    )

    patient03 = get_or_create_patient(
        db,
        username="patient03",
        full_name="Pham Van C",
        email="patient03@clinic.local",
        phone="0911111113",
        gender=Gender.MALE,
        dob=date(2000, 2, 10),
        address="Thu Duc, TP.HCM",
    )

    paracetamol = get_or_create_medicine(
        db,
        name="Paracetamol 500mg",
        unit="Vien",
        price=Decimal("2000.00"),
        stock_qty=100,
    )

    amoxicillin = get_or_create_medicine(
        db,
        name="Amoxicillin 500mg",
        unit="Vien",
        price=Decimal("3500.00"),
        stock_qty=50,
    )

    vitamin_c = get_or_create_medicine(
        db,
        name="Vitamin C 500mg",
        unit="Vien",
        price=Decimal("1500.00"),
        stock_qty=100,
    )

    discontinued = get_or_create_medicine(
        db,
        name="Thuoc mau Discontinued Test",
        unit="Hop",
        price=Decimal("10000.00"),
        stock_qty=10,
        status=MedicineStatus.DISCONTINUED,
    )

    return {
        "admin": admin,
        "receptionist": receptionist,
        "doctor01": doctor01,
        "doctor02": doctor02,
        "doctor03": doctor03,
        "patient01": patient01,
        "patient02": patient02,
        "patient03": patient03,
        "cardio": cardio,
        "pediatrics": pediatrics,
        "dermatology": dermatology,
        "paracetamol": paracetamol,
        "amoxicillin": amoxicillin,
        "vitamin_c": vitamin_c,
        "discontinued": discontinued,
    }


def seed_schedules_and_appointments(
    db: Session,
    data: dict,
) -> dict:

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    month_ago = today - timedelta(days=25)
    two_months_ago = today - timedelta(days=55)
    tomorrow = today + timedelta(days=1)

    d1 = data["doctor01"].user_id
    d2 = data["doctor02"].user_id
    d3 = data["doctor03"].user_id

    p1 = data["patient01"].user_id
    p2 = data["patient02"].user_id
    p3 = data["patient03"].user_id

    s_today_d1 = get_or_create_schedule(
        db,
        doctor_id=d1,
        work_date=today,
        start_time=time(8, 0),
        end_time=time(11, 0),
    )

    s_today_d2 = get_or_create_schedule(
        db,
        doctor_id=d2,
        work_date=today,
        start_time=time(13, 0),
        end_time=time(17, 0),
    )

    s_today_d3 = get_or_create_schedule(
        db,
        doctor_id=d3,
        work_date=today,
        start_time=time(15, 0),
        end_time=time(18, 0),
    )

    s_yesterday_d1 = get_or_create_schedule(
        db,
        doctor_id=d1,
        work_date=yesterday,
        start_time=time(8, 0),
        end_time=time(11, 0),
    )

    s_month_d2 = get_or_create_schedule(
        db,
        doctor_id=d2,
        work_date=month_ago,
        start_time=time(8, 0),
        end_time=time(11, 0),
    )

    s_two_month_d3 = get_or_create_schedule(
        db,
        doctor_id=d3,
        work_date=two_months_ago,
        start_time=time(14, 0),
        end_time=time(17, 0),
    )

    s_tomorrow_d2 = get_or_create_schedule(
        db,
        doctor_id=d2,
        work_date=tomorrow,
        start_time=time(13, 0),
        end_time=time(17, 0),
    )

    appt_today_completed = get_or_create_appointment(
        db,
        schedule_id=s_today_d1.schedule_id,
        patient_id=p1,
        appointment_time=datetime.combine(
            today,
            time(9, 0)
        ),
        status=AppointmentStatus.COMPLETED,
        created_by=AppointmentCreatedBy.PATIENT,
        note="Kham lai dau nguc.",
    )

    appt_today_pending = get_or_create_appointment(
        db,
        schedule_id=s_today_d2.schedule_id,
        patient_id=p3,
        appointment_time=datetime.combine(
            today,
            time(16, 0)
        ),
        status=AppointmentStatus.PENDING,
        created_by=AppointmentCreatedBy.PATIENT,
        note="Kham suc khoe.",
    )

    appt_today_confirmed = get_or_create_appointment(
        db,
        schedule_id=s_today_d3.schedule_id,
        patient_id=p2,
        appointment_time=datetime.combine(
            today,
            time(16, 0)
        ),
        status=AppointmentStatus.CONFIRMED,
        created_by=AppointmentCreatedBy.RECEPTIONIST,
        note="Le tan da xac nhan.",
    )

    appt_yesterday_paid = get_or_create_appointment(
        db,
        schedule_id=s_yesterday_d1.schedule_id,
        patient_id=p1,
        appointment_time=datetime.combine(
            yesterday,
            time(9, 30)
        ),
        status=AppointmentStatus.COMPLETED,
        created_by=AppointmentCreatedBy.RECEPTIONIST,
        note="Tai kham.",
    )

    appt_month_unpaid = get_or_create_appointment(
        db,
        schedule_id=s_month_d2.schedule_id,
        patient_id=p2,
        appointment_time=datetime.combine(
            month_ago,
            time(9, 0)
        ),
        status=AppointmentStatus.COMPLETED,
        created_by=AppointmentCreatedBy.RECEPTIONIST,
        note="Kham dinh ky.",
    )

    appt_two_month_paid = get_or_create_appointment(
        db,
        schedule_id=s_two_month_d3.schedule_id,
        patient_id=p3,
        appointment_time=datetime.combine(
            two_months_ago,
            time(15, 0)
        ),
        status=AppointmentStatus.COMPLETED,
        created_by=AppointmentCreatedBy.AI,
        note="Tao boi AI Assistant de phuc vu test.",
    )

    appt_cancelled = get_or_create_appointment(
        db,
        schedule_id=s_tomorrow_d2.schedule_id,
        patient_id=p3,
        appointment_time=datetime.combine(
            tomorrow,
            time(14, 0)
        ),
        status=AppointmentStatus.CANCELLED,
        created_by=AppointmentCreatedBy.RECEPTIONIST,
        note="Test trang thai Cancelled.",
    )

    chat_session = get_or_create_chat_session(
        db,
        patient_id=p1,
        appointment_id=appt_today_pending.appointment_id,
    )

    existing_messages = db.execute(
        select(ChatMessage).where(
            ChatMessage.session_id == chat_session.session_id
        )
    ).scalars().all()

    if not existing_messages:

        db.add_all([
            ChatMessage(
                session_id=chat_session.session_id,
                sender_type=ChatSenderType.PATIENT,
                content="Toi muon dat lich voi bac si.",
                intent="book_appointment",
            ),
            ChatMessage(
                session_id=chat_session.session_id,
                sender_type=ChatSenderType.AI,
                content="Toi da ho tro tim lich phu hop.",
                intent="book_appointment",
            ),
        ])

    return {
        "appt_today_completed": appt_today_completed,
        "appt_today_pending": appt_today_pending,
        "appt_today_confirmed": appt_today_confirmed,
        "appt_yesterday_paid": appt_yesterday_paid,
        "appt_month_unpaid": appt_month_unpaid,
        "appt_two_month_paid": appt_two_month_paid,
        "appt_cancelled": appt_cancelled,
    }


def seed_medical_records_prescriptions_invoices(
    db: Session,
    data: dict,
    appointments: dict,
) -> None:

    now = datetime.now()

    paracetamol = data["paracetamol"]
    amoxicillin = data["amoxicillin"]
    vitamin_c = data["vitamin_c"]

    # ---------------------------------------------------------
    # Appointment 1
    # Completed + MedicalRecord + Prescription + Invoice Paid
    # ---------------------------------------------------------

    appt1 = appointments["appt_today_completed"]

    record1 = get_or_create_record(
        db,
        appointment_id=appt1.appointment_id,
        symptoms="Dau dau nhe, met moi.",
        diagnosis="Cang thang va mat ngu nhe.",
        note="Theo doi them 1 tuan.",
        examined_at=datetime.combine(
            appt1.appointment_time.date(),
            time(9, 20),
        ),
    )

    get_or_create_prescription(
        db,
        record_id=record1.record_id,
        details=[
            {
                "medicine_id": paracetamol.medicine_id,
                "quantity": 2,
                "dosage": "1 vien moi lan, ngay 2 lan",
                "usage_note": "Uong sau an.",
            },
            {
                "medicine_id": amoxicillin.medicine_id,
                "quantity": 1,
                "dosage": "1 vien moi ngay",
                "usage_note": "Uong sau an toi.",
            },
        ],
    )

    invoice1_total = (
        Decimal("100000.00")
        + paracetamol.price * 2
        + amoxicillin.price
    )

    get_or_create_invoice(
        db,
        appointment_id=appt1.appointment_id,
        total_amount=invoice1_total,
        status=InvoiceStatus.PAID,
        payment_method=PaymentMethod.CASH,
        paid_at=now - timedelta(hours=4),
    )

    # ---------------------------------------------------------
    # Appointment 2
    # Completed + MedicalRecord + Prescription + Invoice Paid
    # ---------------------------------------------------------

    appt2 = appointments["appt_yesterday_paid"]

    record2 = get_or_create_record(
        db,
        appointment_id=appt2.appointment_id,
        symptoms="Ho, dau hong.",
        diagnosis="Viem hong cap.",
        note="Uong du nuoc, nghi ngoi.",
        examined_at=appt2.appointment_time + timedelta(minutes=20),
    )

    get_or_create_prescription(
        db,
        record_id=record2.record_id,
        details=[
            {
                "medicine_id": vitamin_c.medicine_id,
                "quantity": 2,
                "dosage": "1 vien moi ngay",
                "usage_note": "Uong sau an sang.",
            },
        ],
    )

    invoice2_total = (
        Decimal("100000.00")
        + vitamin_c.price * 2
    )

    get_or_create_invoice(
        db,
        appointment_id=appt2.appointment_id,
        total_amount=invoice2_total,
        status=InvoiceStatus.PAID,
        payment_method=PaymentMethod.ONLINE,
        paid_at=now - timedelta(days=1),
    )

    # ---------------------------------------------------------
    # Appointment 3
    # Completed + Prescription + Invoice UNPAID
    # Dung de test /pay
    # ---------------------------------------------------------

    appt3 = appointments["appt_month_unpaid"]

    record3 = get_or_create_record(
        db,
        appointment_id=appt3.appointment_id,
        symptoms="Dau bung nhe sau khi an.",
        diagnosis="Roi loan tieu hoa.",
        note="Dieu chinh che do an uong.",
        examined_at=appt3.appointment_time + timedelta(minutes=20),
    )

    get_or_create_prescription(
        db,
        record_id=record3.record_id,
        details=[
            {
                "medicine_id": paracetamol.medicine_id,
                "quantity": 1,
                "dosage": "1 vien khi dau",
                "usage_note": "Khong qua 3 vien/ngay.",
            },
            {
                "medicine_id": vitamin_c.medicine_id,
                "quantity": 1,
                "dosage": "1 vien moi ngay",
                "usage_note": "Uong sau an.",
            },
        ],
    )

    invoice3_total = (
        Decimal("100000.00")
        + paracetamol.price
        + vitamin_c.price
    )

    get_or_create_invoice(
        db,
        appointment_id=appt3.appointment_id,
        total_amount=invoice3_total,
        status=InvoiceStatus.UNPAID,
        payment_method=None,
        paid_at=None,
    )

    # ---------------------------------------------------------
    # Appointment 4
    # Completed + MedicalRecord + Invoice Paid
    # Khong co prescription
    # ---------------------------------------------------------

    appt4 = appointments["appt_two_month_paid"]

    get_or_create_record(
        db,
        appointment_id=appt4.appointment_id,
        symptoms="Kham da.",
        diagnosis="Viem da tiep xuc nhe.",
        note="Tranh chat kich ung.",
        examined_at=appt4.appointment_time + timedelta(minutes=20),
    )

    get_or_create_invoice(
        db,
        appointment_id=appt4.appointment_id,
        total_amount=Decimal("100000.00"),
        status=InvoiceStatus.PAID,
        payment_method=PaymentMethod.CASH,
        paid_at=now - timedelta(days=55),
    )

    # Ton kho sau 2 invoice Paid trong seed.
    # Paracetamol: 100 -> 98
    # Amoxicillin: 50 -> 49
    # Vitamin C: 100 -> 98
    if paracetamol.stock_qty >= 100:
        paracetamol.stock_qty -= 2

    if amoxicillin.stock_qty >= 50:
        amoxicillin.stock_qty -= 1

    if vitamin_c.stock_qty >= 100:
        vitamin_c.stock_qty -= 2


def main() -> None:

    db = SessionLocal()

    try:

        print("=== Seed Clinic Management System ===")

        catalog = seed_users_and_catalog(db)

        appointments = seed_schedules_and_appointments(
            db,
            catalog,
        )

        seed_medical_records_prescriptions_invoices(
            db,
            catalog,
            appointments,
        )

        db.commit()

        print("\nSeed completed.\n")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

if __name__ == "__main__":
    main()
