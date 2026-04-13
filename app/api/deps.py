from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token, oauth2_scheme
from app.models.user import User
from app.models.user_factory import UserFactory

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("user_id")
    permissions = payload.get("permissions", [])
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()

    print("TOKEN PAYLOAD:", payload)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # attach permissions
    user.permissions = permissions

    # 🔥 LOAD FACTORIES
    factories = db.query(UserFactory).filter(
        UserFactory.user_id == user.id
    ).all()

    user.factory_ids = [f.factory_id for f in factories]
    user.factory_names = [f.factory_name for f in factories]
    
    return user
