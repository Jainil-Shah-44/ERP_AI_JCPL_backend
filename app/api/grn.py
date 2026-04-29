from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from uuid import UUID

from app.db.session import get_db
from app.api.deps import get_current_user
from sqlalchemy.orm import joinedload
from app.schemas.grn.grn import GRNCreate
from app.services.grn.grn_service import (
    create_grn_draft,
    submit_grn,
    get_total_received_qty,
    update_grn,
    cancel_grn
)

from app.models.grn.grn import GRN
from app.models.grn.grn_item import GRNItem
from app.models.purchase.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.api.dependencies.permission import require_permission
from app.services.grn.grn_pdf_service import generate_grn_pdf

router = APIRouter(prefix="/api/grn", tags=["GRN"])

FULL_ACCESS_ROLES = ["admin", "superadmin", "manager"]
# ============================================
# CREATE GRN (DRAFT)
# ============================================
@router.post("/", dependencies=[Depends(require_permission("GRN_PROCESS"))])
def create_grn_api(
    payload: GRNCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return create_grn_draft(db, payload, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# SUBMIT GRN
# ============================================
@router.post("/{grn_id}/submit", dependencies=[Depends(require_permission("GRN_PROCESS"))])
def submit_grn_api(
    grn_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return submit_grn(db, grn_id, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# LIST GRN
# ============================================
# @router.get("/")
# def list_grn(
#     db: Session = Depends(get_db),
#     user=Depends(get_current_user),
#     skip: int = 0,
#     limit: int = 20,
#     factory_id: str | None = None
# ):
#     query = db.query(GRN).filter(GRN.company_id == user.company_id)

#     # 🔥 FACTORY FILTER FROM USER ACCESS
#     if user.role.lower() not in FULL_ACCESS_ROLES:
#         query = query.filter(GRN.factory_id.in_(user.factory_ids))

#     # 🔥 FACTORY FILTER FROM DROPDOWN
#     if factory_id:
#         query = query.filter(GRN.factory_id == factory_id)

#     total = query.count()

#     records = query.order_by(GRN.created_at.desc()).offset(skip).limit(limit).all()

#     return {
#         "total": total,
#         "data": [
#             {
#                 "id": grn.id,
#                 "grn_number": grn.grn_number,
#                 "status": grn.status,
#                 "created_at": grn.created_at,
#                 "factory_name": grn.factory.name if grn.factory else None,
#                 "plot_no": grn.po.plot_no if grn.po else None
#             }
#             for grn in records
#         ]
#     }

@router.get("/")
def list_grn(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    status: str | None = None,
    skip: int = 0,
    limit: int = 20,
    factory_id: str | None = None
):
    query = db.query(GRN).filter(GRN.company_id == user.company_id)

    # FACTORY FILTER FROM USER ACCESS
    if user.role.lower() not in FULL_ACCESS_ROLES:
        query = query.filter(GRN.factory_id.in_(user.factory_ids))

    # FACTORY FILTER FROM DROPDOWN
    if factory_id:
        query = query.filter(GRN.factory_id == factory_id)

    # STATUS FILTER (NEW ADDITION)
    if status and status.upper() != "ALL":
        query = query.filter(GRN.status == status.upper())

    total = query.count()

    records = query.order_by(GRN.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "data": [
            {
                "id": grn.id,
                "grn_number": grn.grn_number,
                "status": grn.status,
                "created_at": grn.created_at,
                "factory_name": grn.factory.name if grn.factory else None,
                "plot_no": grn.po.plot_no if grn.po else None
            }
            for grn in records
        ]
    }

@router.get("/available-pos")
def get_available_pos(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
   
    if user.role.lower() in FULL_ACCESS_ROLES:
        pos_query = db.query(PurchaseOrder).options(
            joinedload(PurchaseOrder.vendor),
            joinedload(PurchaseOrder.factory)
        ).filter(
            PurchaseOrder.company_id == user.company_id
        )
    else:
        pos_query = db.query(PurchaseOrder).options(
            joinedload(PurchaseOrder.vendor),
            joinedload(PurchaseOrder.factory)
        ).filter(
            PurchaseOrder.company_id == user.company_id,
            PurchaseOrder.factory_id.in_(user.factory_ids)
        )

    pos = pos_query.all()

    result = []

    for po in pos:
        items = db.query(PurchaseOrderItem).filter(
            PurchaseOrderItem.po_id == po.id
        ).all()

        total_ordered = Decimal(0)
        total_received = Decimal(0)

        for item in items:
            received = get_total_received_qty(db, item.id)

            total_ordered += Decimal(item.quantity or 0)
            total_received += Decimal(received or 0)

        # 🔥 DETERMINE STATUS
        if total_received == 0:
            po_status = "REMAINING"
        elif total_received < total_ordered:
            po_status = "PARTIAL"
        else:
            po_status = "COMPLETED"

        # 👉 Only show if not completed (optional)
        if po_status != "COMPLETED":
            result.append({
                "id": po.id,
                "plot_no": po.plot_no,
                "vendor_name": po.vendor.name if po.vendor else None,
                "status": po.status,
                "grn_status": po_status,   # 🔥 NEW FIELD
                "created_at": po.created_at,
                "factory_id": po.factory_id,
                "factory_name": po.factory.name if po.factory else None
            })

    return result




# ============================================
# GRN DETAIL
# ============================================
@router.get("/{grn_id}")
def get_grn_detail(
    grn_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    

    grn = (
        db.query(GRN)
        .options(
            joinedload(GRN.items).joinedload(GRNItem.material),
            joinedload(GRN.items).joinedload(GRNItem.unit),
            joinedload(GRN.po),
            joinedload(GRN.vendor),
            joinedload(GRN.factory),
            joinedload(GRN.items).joinedload(GRNItem.po_item),
        )
        .filter(
            GRN.id == grn_id,
            GRN.company_id == user.company_id
        )
        .first()
    )

    if not grn:
        raise HTTPException(status_code=404, detail="GRN not found")

    return {
        "id": grn.id,
        "grn_number": grn.grn_number,
        "status": grn.status,
        "created_at": grn.created_at,
        "po_id": grn.po_id,
        "plot_no": grn.po.plot_no if grn.po else None,
        "vendor_name": grn.vendor.name if grn.vendor else None,
        "factory_id": grn.factory_id,
        "factory_name": grn.factory.name if grn.factory else None,
        "remarks": grn.remarks,

        "items": [   # ✅ IMPORTANT KEY NAME
            {

                "po_item_id": item.po_item_id,   # ✅ ADD
                "material_id": item.material_id, # ✅ ADD
                "unit_id": item.unit_id,         # ✅ ADD
                "material_name": (
                    item.material.material_name
                    if item.material
                    else item.po_item.material_name   # ✅ FIX
                ),
                "specification": (
                    item.po_item.specification
                    if item.po_item and item.po_item.specification
                    else None
                ),
                "description": (
                    item.po_item.description
                    if item.po_item else None
                ),
                "unit_name": (
                    item.unit.unit_code
                    if item.unit
                    else item.po_item.unit_name       # ✅ FIX
                ),
                "ordered_qty": item.ordered_qty,
                "received_qty": item.received_qty,
                "accepted_qty": item.accepted_qty,
                "rejected_qty": item.rejected_qty,
                "batch_number": item.batch_number,
            }
            for item in grn.items
        ]
    }
# ============================================
# GET PO PENDING ITEMS
# ============================================
@router.get("/po/{po_id}/pending-items")
def get_po_pending_items(
    po_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user), 
    grn_id: str | None = None
):
    po = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == po_id,
        PurchaseOrder.company_id == user.company_id
    ).first()

    if not po:
        raise HTTPException(status_code=404, detail="PO not found")

    items = db.query(PurchaseOrderItem).filter(
        PurchaseOrderItem.po_id == po_id
    ).all()

    result = []

    for item in items:
        total_received = get_total_received_qty(
                db,
                item.id,
                exclude_grn_id=grn_id  # for create
            )
        pending_qty = Decimal(item.quantity) - Decimal(total_received)

        if pending_qty > 0:
            result.append({
                "po_item_id": item.id,
                "material_id": item.material_id,
                "material_name": (
                    item.material.material_name
                    if item.material
                    else item.material_name
                ),
                "specification": item.specification,
                "description": item.description,
                "unit_name": (
                    item.unit.unit_code
                    if item.unit
                    else item.unit_name
                ),
                "unit_id": item.unit_id,
                "ordered_qty": item.quantity,
                "received_qty": total_received,
                "pending_qty": pending_qty
            })

    return result


@router.put("/{grn_id}", dependencies=[Depends(require_permission("GRN_PROCESS"))])
def update_grn_api(
    grn_id: str,
    payload: GRNCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return update_grn(db, grn_id, payload, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{grn_id}/pdf")
def download_grn_pdf(grn_id: UUID, db: Session = Depends(get_db)):
    return generate_grn_pdf(db, grn_id)


@router.post("/{grn_id}/cancel", dependencies=[Depends(require_permission("GRN_PROCESS"))])
def cancel_grn_api(
    grn_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return cancel_grn(db, grn_id, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))