from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import vendor as crud
from app.schemas.vendor import VendorCreate, VendorUpdate, VendorRead
from app.api.deps import get_db, get_current_user
from app.api.dependencies.permission import require_any_permission
from app.models.vendor import Vendor


router = APIRouter(
    prefix="/api/masters/vendors",
    tags=["Vendor"],
    )
@router.post("/", response_model=VendorRead, status_code=201)
def create(payload: VendorCreate, db: Session = Depends(get_db), user=Depends(get_current_user), _ = Depends(require_any_permission("VENDOR_EDIT","MASTER_EDIT"))):
    return crud.create(db=db, company_id=user.company_id, obj_in=payload.dict())

@router.get("/", response_model=list[VendorRead])
def list_all(db: Session = Depends(get_db), user=Depends(get_current_user),_ = Depends(require_any_permission("MASTER_VIEW","MASTER_EDIT"))):
    return crud.list(db=db, company_id=user.company_id)


@router.get("/search")
def search_vendors(
    search: str = "",
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    query = db.query(Vendor).filter(
        Vendor.company_id == user.company_id
    )

    if search:
        query = query.filter(
            Vendor.name.ilike(f"%{search}%")
        )

    vendors = query.limit(20).all()

    return [
        {
            "id": str(v.id),
            "name": v.name,
            "contact_number": v.contact_number,
            "address_line1": v.address_line2,
            "address_line2": v.address_line3,
        }
        for v in vendors
    ]

@router.get("/paginated")
def get_vendors_paginated(
    search: str = "",
    page: int = 1,
    limit: int = 5,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    _ = Depends(require_any_permission("MASTER_VIEW","MASTER_EDIT"))
):
    query = db.query(Vendor).filter(
        Vendor.company_id == user.company_id
    )

    if search:
        query = query.filter(
            Vendor.name.ilike(f"%{search}%")
        )

    total = query.count()

    vendors = (
        query.order_by(Vendor.name)
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": [
            {
                "id": str(v.id),
                "name": v.name,
                "email": v.email,  # important for next step
                "contact_number": v.contact_number,
                "address_line1": v.address_line1,
                "address_line2": v.address_line2,
            }
            for v in vendors
        ]
    }

@router.patch("/{id}/email")
def update_vendor_email(
    id: UUID,
    payload: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    _=Depends(require_any_permission("VENDOR_EDIT","MASTER_EDIT"))
):
    vendor = db.query(Vendor).filter(
        Vendor.id == id,
        Vendor.company_id == user.company_id
    ).first()

    if not vendor:
        raise HTTPException(404, "Vendor not found")

    vendor.email = payload.get("email")

    db.commit()

    return {"message": "Email updated"}


@router.get("/{id}", response_model=VendorRead)
def get(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user),_ = Depends(require_any_permission("MASTER_VIEW","MASTER_EDIT"))):
    obj = crud.get(db=db, id=id, company_id=user.company_id)
    if not obj:
        raise HTTPException(404, "Vendor not found")
    return obj

@router.put("/{id}", response_model=VendorRead)
def update(id: UUID, payload: VendorUpdate, db: Session = Depends(get_db), user=Depends(get_current_user), _ = Depends(require_any_permission("VENDOR_EDIT","MASTER_EDIT"))):
    obj = crud.get(db=db, id=id, company_id=user.company_id)
    if not obj:
        raise HTTPException(404, "Vendor not found")
    return crud.update(db=db, db_obj=obj, obj_in=payload.dict(exclude_unset=True))

@router.delete("/{id}", status_code=204)
def delete(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user), _ = Depends(require_any_permission("VENDOR_EDIT","MASTER_EDIT"))):
    if not crud.remove(db=db, id=id, company_id=user.company_id):
        raise HTTPException(404, "Vendor not found")


