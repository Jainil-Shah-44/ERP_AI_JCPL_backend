from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.services.purchase.po_list_service import get_po_list
from app.services.purchase.po_detail_service import get_po_detail
from app.services.purchase.po_status_service import release_po
from app.services.purchase.po_status_service import cancel_po


router = APIRouter(prefix="/purchase-order", tags=["Purchase Order"])


@router.get("/")
def list_po(
    status: str | None = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return get_po_list(db, user, status, page, limit)


@router.get("/{po_id}")
def get_po(
    po_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return get_po_detail(db, po_id, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{po_id}/release")
def release_po_endpoint(
    po_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return release_po(db, po_id, user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{po_id}/cancel")
def cancel_po_endpoint(
    po_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return cancel_po(db, po_id, user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
