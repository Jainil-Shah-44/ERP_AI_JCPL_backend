from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import LoginRequest
from fastapi.responses import JSONResponse
from app.models.user import User
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.refresh import save_refresh_token, revoke_refresh_token
from app.models.refresh_token import RefreshToken
from datetime import datetime
import uuid



router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.company_code == data.company_code,
        User.username == data.username,
        User.is_active == True
    ).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Access token
    access_token = create_access_token({
        "user_id": str(user.id),
        "company_code": user.company_code
    })

    # Refresh token (UUID, not JWT)
    refresh_token = str(uuid.uuid4())
    save_refresh_token(db, user.id, refresh_token)

    response = JSONResponse({
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "username": user.username,
            "company_code": user.company_code
        }
    })

    # 🔑 THIS COOKIE MUST APPEAR
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,      # MUST be False on localhost
        samesite="lax",
        path="/"
    )

    return response


@router.post("/refresh")
def refresh_token(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")

    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")

    rt = db.query(RefreshToken).filter(
        RefreshToken.token == token,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()

    if not rt:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({
        "user_id": str(rt.user_id)
    })

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        revoke_refresh_token(db, refresh_token)

    response = JSONResponse({"message": "Logged out"})
    response.delete_cookie("refresh_token", path="/")
    return response
