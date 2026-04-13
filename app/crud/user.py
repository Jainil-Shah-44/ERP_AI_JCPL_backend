from sqlalchemy.orm import Session
from uuid import UUID

from app.models.user import User
from app.core.security import hash_password
from app.models.role import Role
from app.models.user_role import UserRole
from fastapi import HTTPException
from app.models.factory import Factory
from app.models.user_factory import UserFactory


def create_user(db: Session, *, data, current_user):

    user = User(
        username=data.username,
        email=data.email,
        mobile_number=data.mobile_number,
        role=data.role,
        location=data.location,

        company_id=current_user.company_id,
        company_code=current_user.company_code,

        password_hash=hash_password(data.password),
        is_active=True,
    )



    db.add(user)
    db.flush()   # gets user.id before commit

        
    # get role from role table
    role = db.query(Role).filter(Role.name == data.role).first()

    if not role:
        raise HTTPException(status_code=400, detail="Invalid role")

    user_role = UserRole(
        user_id=user.id,
        role_id=role.id
    )

    db.add(user_role)

    # 🔥 assign factories
    for factory_id in (data.factory_ids or []):
        factory = db.query(Factory).filter(Factory.id == factory_id).first()

        db.add(UserFactory(
            user_id=user.id,
            factory_id=factory_id,
            factory_name=factory.name if factory else None
        ))


    db.commit()
    db.refresh(user)

    user.role = role.name

    return user

def get_users(db: Session, *, company_id):

    users = (
        db.query(User, Role.name.label("role"))
        .join(UserRole, UserRole.user_id == User.id)
        .join(Role, Role.id == UserRole.role_id)
        .filter(User.company_id == company_id)
        .all()
    )

    result = []

    for user, role in users:
        factories = db.query(UserFactory).filter(
            UserFactory.user_id == user.id
        ).all()

        user.factory_ids = [f.factory_id for f in factories]
        user.role = role
        result.append(user)

    return result

def get_user(db: Session, *, user_id: UUID, company_id):

    result = (
        db.query(User, Role.name.label("role"))
        .join(UserRole, UserRole.user_id == User.id)
        .join(Role, Role.id == UserRole.role_id)
        .filter(
            User.id == user_id,
            User.company_id == company_id
        )
        .first()
    )

    if not result:
        return None

    user, role = result
    user.role = role

    

    factories = db.query(UserFactory).filter(
        UserFactory.user_id == user.id
    ).all()

    user.factory_ids = [f.factory_id for f in factories]

    return user

def update_user(db: Session, *, user: User, data):

    update_data = data.dict(exclude_unset=True)

    if "role" in update_data:
        role = db.query(Role).filter(Role.name == update_data["role"]).first()

        if not role:
            raise HTTPException(status_code=400, detail="Invalid role")

        user_role = db.query(UserRole).filter(
            UserRole.user_id == user.id
        ).first()

        user_role.role_id = role.id
        user.role = update_data["role"]  # 👈 keep user table synced

        del update_data["role"]

    for field, value in update_data.items():
        if field == "password":
            continue
        setattr(user, field, value)

    

    if "factory_ids" in data.dict(exclude_unset=True):

        # delete old
        db.query(UserFactory).filter(
            UserFactory.user_id == user.id
        ).delete()

        # add new
        for factory_id in (data.factory_ids or []):
            factory = db.query(Factory).filter(Factory.id == factory_id).first()

            db.add(UserFactory(
                user_id=user.id,
                factory_id=factory_id,
                factory_name=factory.name if factory else None
            ))

    db.commit()
    db.refresh(user)

    
    

    role = (
        db.query(Role.name)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user.id)
        .first()
    )

    user.role = role[0] if role else None

    factories = db.query(UserFactory).filter(
        UserFactory.user_id == user.id
    ).all()

    user.factory_ids = [f.factory_id for f in factories]

    return user

def delete_user(db: Session, *, user: User):
    db.delete(user)
    db.commit()

