from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import group as crud
from app.schemas.group import GroupCreate, GroupUpdate, GroupRead
from app.api.deps import get_db, get_current_user

router = APIRouter(prefix="/masters/groups", tags=["Group"])

@router.post("/", response_model=GroupRead, status_code=201)
def create(payload: GroupCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.create(db=db, company_id=user.company_id, obj_in=payload.dict())

@router.get("/", response_model=list[GroupRead])
def list_all(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.list(db=db, company_id=user.company_id)

@router.get("/{id}", response_model=GroupRead)
def get(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = crud.get(db=db, id=id, company_id=user.company_id)
    if not obj:
        raise HTTPException(404, "Group not found")
    return obj

@router.put("/{id}", response_model=GroupRead)
def update(id: UUID, payload: GroupUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = crud.get(db=db, id=id, company_id=user.company_id)
    if not obj:
        raise HTTPException(404, "Group not found")
    return crud.update(db=db, db_obj=obj, obj_in=payload.dict(exclude_unset=True))

@router.delete("/{id}", status_code=204)
def delete(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not crud.remove(db=db, id=id, company_id=user.company_id):
        raise HTTPException(404, "Group not found")
