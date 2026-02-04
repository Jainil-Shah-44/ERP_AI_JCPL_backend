from sqlalchemy.orm import Session
from uuid import UUID

from app.models.user import User
from app.core.security import hash_password

def create_user(db: Session, *, data, current_user):
    user = User(
        username=data.username,
        email=data.email,
        mobile_number=data.mobile_number,
        role=data.role,
        location=data.location,

        company_id=current_user.company_id,      # ✅ ERP source of truth
        company_code=current_user.company_code,  # legacy / display

        password_hash=hash_password(data.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_users(db: Session, *, company_id):
    return db.query(User).filter(
        User.company_id == company_id,
        #User.is_active == True
    ).all()


def get_user(db: Session, *, user_id: UUID, company_id):
    return db.query(User).filter(
        User.id == user_id,
        User.company_id == company_id,
        #User.is_active == True
    ).first()


def update_user(db: Session, *, user: User, data):
    for field, value in data.dict(exclude_unset=True).items():
        if field == "password":
            continue
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, *, user: User):
    db.delete(user)
    db.commit()

