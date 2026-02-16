from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.company import Company
from app.models.user import User
from app.core.security import hash_password

COMPANY_CODE = "JEEVAN01"
ADMIN_USERNAME = "admin3"
ADMIN_PASSWORD = "admin123"
ADMIN_ROLE = "SUPERADMIN"


def create_admin_user():
    db: Session = SessionLocal()

    try:
        # 1️⃣ Fetch Existing Company
        company = (
            db.query(Company)
            .filter(Company.company_code == COMPANY_CODE)
            .first()
        )

        if not company:
            print(f"❌ Company '{COMPANY_CODE}' not found.")
            return

        print(f"ℹ️ Company found: {company.company_code}")

        # 2️⃣ Check If User Already Exists
        existing_user = (
            db.query(User)
            .filter(
                User.username == ADMIN_USERNAME,
                User.company_id == company.id,
            )
            .first()
        )

        if existing_user:
            print("ℹ️ Admin user already exists.")
            return

        # 3️⃣ Create Admin User
        hashed_password = hash_password(ADMIN_PASSWORD)

        admin_user = User(
            company_id=company.id,
            company_code=company.company_code,
            username=ADMIN_USERNAME,
            email=None,
            mobile_number=None,
            role=ADMIN_ROLE,
            location=None,
            password_hash=hashed_password,
            is_active=True,
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("✅ Admin user created successfully.")

    except Exception as e:
        db.rollback()
        print("❌ Error:", str(e))

    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
