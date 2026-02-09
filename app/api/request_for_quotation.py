from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.purchase.request_for_quotation import RFQCreate
from app.services.purchase.request_for_quotation_service import create_rfq_from_pr
from typing import List
from uuid import UUID
from app.services.purchase.rfq_vendor_invite_service import invite_vendors_to_rfq
from app.schemas.purchase.rfq_vendor_quotation import RFQVendorQuotationCreate
from app.services.purchase.rfq_vendor_quotation_service import submit_vendor_quotation
from app.services.purchase.rfq_comparison_service import get_rfq_comparison_matrix
from app.schemas.purchase.po_from_rfq import POFromRFQCreate
from app.services.purchase.po_from_rfq_service import create_po_from_rfq_selection

router = APIRouter(prefix="/rfq", tags=["RFQ"])


@router.post("/")
def create_rfq(
    payload: RFQCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return create_rfq_from_pr(db, payload, user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{rfq_id}/invite-vendors")
def invite_vendors(
    rfq_id: UUID,
    vendor_ids: List[UUID],
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return invite_vendors_to_rfq(db, rfq_id, vendor_ids, user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/vendor/submit-quotation")
def submit_quotation(
    payload: RFQVendorQuotationCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return submit_vendor_quotation(db, payload, user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{rfq_id}/comparison")
def get_rfq_comparison(
    rfq_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return get_rfq_comparison_matrix(db, rfq_id, user)

@router.post("/{rfq_id}/create-po")
def create_po_from_rfq(
    payload: POFromRFQCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return create_po_from_rfq_selection(db, payload, user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))