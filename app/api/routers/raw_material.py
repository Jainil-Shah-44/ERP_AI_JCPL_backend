from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import raw_material as crud
from app.schemas.raw_material import RawMaterialCreate, RawMaterialUpdate, RawMaterialRead
from app.api.deps import get_db, get_current_user
from app.api.dependencies.permission import require_any_permission

router = APIRouter(
    prefix="/api/masters/raw-material",
    tags=["Raw Material"],
    )
@router.post("/", response_model=RawMaterialRead, status_code=201)
def create(payload: RawMaterialCreate, db: Session = Depends(get_db), user=Depends(get_current_user),_ = Depends(require_any_permission("RAW_MATERIAL_EDIT","MASTER_EDIT"))):
    return crud.create(db=db, company_id=user.company_id, obj_in=payload.dict())

@router.get("/", response_model=list[RawMaterialRead])
def list_all(db: Session = Depends(get_db), user=Depends(get_current_user),_ = Depends(require_any_permission("MASTER_VIEW","MASTER_EDIT"))):
    return crud.list(db=db, company_id=user.company_id)

@router.get("/{id}", response_model=RawMaterialRead)
def get(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user),_ = Depends(require_any_permission("MASTER_VIEW","MASTER_EDIT"))):
    obj = crud.get(db=db, id=id, company_id=user.company_id)
    if not obj:
        raise HTTPException(404, "Raw material not found")
    return obj

@router.put("/{id}", response_model=RawMaterialRead)
def update(id: UUID, payload: RawMaterialUpdate, db: Session = Depends(get_db), user=Depends(get_current_user),_ = Depends(require_any_permission("RAW_MATERIAL_EDIT","MASTER_EDIT"))):
    obj = crud.get(db=db, id=id, company_id=user.company_id)
    if not obj:
        raise HTTPException(404, "Raw material not found")
    return crud.update(db=db, db_obj=obj, obj_in=payload.dict(exclude_unset=True))

@router.delete("/{id}", status_code=204)
def delete(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user),_ = Depends(require_any_permission("RAW_MATERIAL_EDIT","MASTER_EDIT"))):
    if not crud.remove(db=db, id=id, company_id=user.company_id):
        raise HTTPException(404, "Raw material not found")
