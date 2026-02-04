from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import department as crud
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentRead
from app.api.deps import get_db, get_current_user

router = APIRouter(prefix="/masters/departments", tags=["Department"])

@router.post("/", response_model=DepartmentRead, status_code=201)
def create(payload: DepartmentCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.create(db=db, company_id=user.company_id, obj_in=payload.dict())

@router.get("/", response_model=list[DepartmentRead])
def list_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.list(db=db, company_id=user.company_id, skip=skip, limit=limit)

@router.get("/{id}", response_model=DepartmentRead)
def get(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = crud.get(db=db, id=id, company_id=user.company_id)
    if not obj:
        raise HTTPException(404, "Department not found")
    return obj

@router.put("/{id}", response_model=DepartmentRead)
def update(id: UUID, payload: DepartmentUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = crud.get(db=db, id=id, company_id=user.company_id)
    if not obj:
        raise HTTPException(404, "Department not found")
    return crud.update(db=db, db_obj=obj, obj_in=payload.dict(exclude_unset=True))

@router.delete("/{id}", status_code=204)
def delete(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not crud.remove(db=db, id=id, company_id=user.company_id):
        raise HTTPException(404, "Department not found")
