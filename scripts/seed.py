from sqlalchemy import select

from app.core.security import hash_password
from app.database.connection import SessionLocal
from app.models.enums import UserRole, UserStatus
from app.models.user import User, Admin

def seed_admin() -> None:
    db = SessionLocal()

    try:
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
            type="admin",
        )

        db.add(admin)
        db.commit()

        print("Tao admin thanh cong")
        print("Username: admin")
        print("Password: admin123")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()