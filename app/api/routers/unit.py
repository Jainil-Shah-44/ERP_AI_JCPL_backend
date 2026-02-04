from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import unit as crud
from app.schemas.unit import UnitCreate, UnitUpdate, UnitRead
from app.api.deps import get_db, get_current_user

router = APIRouter(prefix="/masters/units", tags=["Unit"])

@router.post("/", response_model=UnitRead, status_code=201)
def create(payload: UnitCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.create(db=db, company_id=user.company_id, obj_in=payload.dict())

@router.get("/", response_model=list[UnitRead])
def list_all(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.list(db=db, company_id=user.company_id)

@router.get("/{id}", response_model=UnitRead)
def get(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = crud.get(db=db, id=id, company_id=user.company_id)
    if not obj:
        raise HTTPException(404, "Unit not found")
    return obj

@router.put("/{id}", response_model=UnitRead)
def update(id: UUID, payload: UnitUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = crud.get(db=db, id=id, company_id=user.company_id)
    if not obj:
        raise HTTPException(404, "Unit not found")
    return crud.update(db=db, db_obj=obj, obj_in=payload.dict(exclude_unset=True))

@router.delete("/{id}", status_code=204)
def delete(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not crud.remove(db=db, id=id, company_id=user.company_id):
        raise HTTPException(404, "Unit not found")
