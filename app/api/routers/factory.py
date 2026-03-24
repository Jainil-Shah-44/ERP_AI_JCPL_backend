from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import factory as crud
from app.schemas.factory import FactoryCreate, FactoryUpdate, FactoryRead
from app.api.deps import get_db, get_current_user
from app.api.dependencies.permission import require_any_permission
from app.models.factory import Factory

router = APIRouter(prefix="/api/masters/factories", tags=["Factory"])

@router.post("/", response_model=FactoryRead, status_code=201)
def create(payload: FactoryCreate, db: Session = Depends(get_db), user=Depends(get_current_user),_ = Depends(require_any_permission("FACTORY_EDIT","MASTER_EDIT"))):
    return crud.create(db=db, company_id=user.company_id, obj_in=payload.dict())

@router.get("/", response_model=list[FactoryRead])
def list_all(db: Session = Depends(get_db), user=Depends(get_current_user),_ = Depends(require_any_permission("MASTER_VIEW","MASTER_EDIT"))):
    return crud.list(db=db, company_id=user.company_id)


@router.get("/search")
def search_factories(
    search: str = "",
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    query = db.query(Factory).filter(
        Factory.company_id == user.company_id
    )

    if search:
        query = query.filter(
            Factory.name.ilike(f"%{search}%")
        )

    factories = query.limit(20).all()

    return [
        {
            "id": str(f.id),
            "name": f.name,
            "range": f.range_,
            "division": f.division,
            "commissionerate": f.commissionerate,
            "gstin": f.gstin,
        }
        for f in factories
    ]

@router.get("/{id}", response_model=FactoryRead)
def get(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user),_ = Depends(require_any_permission("MASTER_VIEW","MASTER_EDIT"))):
    obj = crud.get(db=db, id=id, company_id=user.company_id)
    if not obj:
        raise HTTPException(404, "Factory not found")
    return obj

@router.put("/{id}", response_model=FactoryRead)
def update(id: UUID, payload: FactoryUpdate, db: Session = Depends(get_db), user=Depends(get_current_user),_ = Depends(require_any_permission("FACTORY_EDIT","MASTER_EDIT"))):
    obj = crud.get(db=db, id=id, company_id=user.company_id)
    if not obj:
        raise HTTPException(404, "Factory not found")
    return crud.update(db=db, db_obj=obj, obj_in=payload.dict(exclude_unset=True))

@router.delete("/{id}", status_code=204)
def delete(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user),_ = Depends(require_any_permission("FACTORY_EDIT","MASTER_EDIT"))):
    if not crud.remove(db=db, id=id, company_id=user.company_id):
        raise HTTPException(404, "Factory not found")




