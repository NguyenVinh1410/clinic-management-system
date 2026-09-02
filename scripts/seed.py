from sqlalchemy import select

from app.core.security import hash_password
from app.database.connection import SessionLocal
from app.models.enums import UserRole, UserStatus, Gender
from app.models.user import User, Admin, Patient

def seed_admin(db) -> None:
    stmt = (
        select(User)
        .where(User.username == "admin")
    )

    existing_user = (
        db.execute(stmt).scalar_one_or_none()
    )

    if existing_user is not None:
        print("Admin da ton tai")
        return

    admin = Admin(
        username="admin",
        password=hash_password("admin123"),
        full_name="System Administrator",
        email="admin@clinic.local",
        phone="0900000000000",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
        #created_at=datetime(2024, 1, 1, 12, 0, 0) 1/1/2024 luc 12:00:00
        type="admin",
    )

    db.add(admin)


def seed_patient(db) -> None:
    stmt = (
        select(User)
        .where(User.username == "patient01")
    )

    existing_user = (
        db.execute(stmt).scalar_one_or_none()
    )

    if existing_user is not None:
        print("Patient da ton tai")
        return

    patient = Patient(
        username="patient01",
        password=hash_password("patient123"),
        full_name="Nguyen Van A",
        email="patient@clinic.local",
        phone="0911111111",
        role=UserRole.PATIENT,
        status=UserStatus.ACTIVE,
        type="patient",
        dob=None,
        address="HCM city",
    )

    db.add(patient)


def main() -> None:
    db = SessionLocal()

    try:
        # seed_admin(db)
        seed_patient(db)

        db.commit()

        print("seed completed.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
