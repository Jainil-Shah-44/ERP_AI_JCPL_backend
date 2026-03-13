from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.core.permissions import get_user_permissions


def require_permission(code: str):

    def checker(current_user = Depends(get_current_user)):

        if code not in current_user.permissions:
            raise HTTPException(
                status_code=403,
                detail="Permission denied"
            )

        return current_user

    return checker

def require_any_permission(*codes):

    def checker(current_user = Depends(get_current_user)):

        if not any(c in current_user.permissions for c in codes):
            raise HTTPException(
                status_code=403,
                detail="Permission denied"
            )

        return current_user

    return checker