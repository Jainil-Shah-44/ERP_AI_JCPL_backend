from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.user import UserCreate, UserUpdate, UserRead
from app.crud.user import (
    create_user,
    get_users,
    get_user,
    update_user,
    delete_user,
)

router = APIRouter(
    prefix="/masters/users",
    tags=["User Master"]
)

@router.post("/", response_model=UserRead, status_code=201)
def create(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_user(
        db=db,
        data=payload,
        current_user=current_user,
    )


@router.get("/", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_users(
        db=db,
        company_id=current_user.company_id
    )


@router.get("/{user_id}", response_model=UserRead)
def get_one(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = get_user(
        db=db,
        user_id=user_id,
        company_id=current_user.company_id
    )
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.put("/{user_id}", response_model=UserRead)
def update(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = get_user(
        db=db,
        user_id=user_id,
        company_id=current_user.company_id  # ✅ FIX
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return update_user(db=db, user=user, data=payload)

@router.delete("/{user_id}", status_code=204)
def delete(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = get_user(
        db=db,
        user_id=user_id,
        company_id=current_user.company_id
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    delete_user(db=db, user=user)
