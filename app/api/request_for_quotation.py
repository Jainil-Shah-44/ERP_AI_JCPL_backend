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
from app.services.purchase.rfq_list_service import get_rfq_list
from app.services.purchase.rfq_detail_service import get_rfq_detail
from app.services.purchase.rfq_cancel_service import cancel_rfq
from app.services.purchase.rfq_detail_service import get_rfq_vendors
from app.api.dependencies.permission import require_permission
from app.models.purchase.request_for_quotation import RequestForQuotation
from app.models.purchase.request_for_quotation_vendor import RequestForQuotationVendor
from app.services.purchase.rfq_email_service import send_rfq_email
from app.models.vendor import Vendor
from app.models.purchase.request_for_quotation_vendor import RequestForQuotationVendor
from app.models.purchase.request_for_quotation import RequestForQuotation
from app.services.purchase.rfq_email_service import send_rfq_email
from app.models.vendor import Vendor
from app.models.purchase.purchase_requisition_attachment import PurchaseRequisitionAttachment
from fastapi import HTTPException
import os
from app.models.purchase.request_for_quotation_attachment import RequestForQuotationAttachment
from app.services.purchase.rfq_vendor_quotation_service import get_vendor_quotation


router = APIRouter(prefix="/api/rfq", tags=["RFQ"])


@router.post("/",dependencies=[Depends(require_permission("RFQ_CREATE"))])
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


@router.post("/{rfq_id}/invite-vendors",dependencies=[Depends(require_permission("RFQ_INVITE_VENDOR"))])
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
    
@router.get("/{rfq_id}/comparison",dependencies=[Depends(require_permission("RFQ_COMPARISON"))])
def get_rfq_comparison(
    rfq_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return get_rfq_comparison_matrix(db, rfq_id, user)

@router.post("/{rfq_id}/create-po",dependencies=[Depends(require_permission("RFQ_CREATE_PO"))])
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
    
@router.get("/",dependencies=[Depends(require_permission("RFQ_VIEW"))])
def list_rfq(
    status: str | None = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return get_rfq_list(db, user, status, page, limit)


@router.get("/{rfq_id}")
def get_rfq(
    rfq_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return get_rfq_detail(db, rfq_id, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{rfq_id}/cancel")
def cancel_rfq_endpoint(
    rfq_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return cancel_rfq(db, rfq_id, user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{rfq_id}/vendors")
def get_vendors(
    rfq_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return get_rfq_vendors(db, rfq_id, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{rfq_id}/vendor/{rfq_vendor_id}")
def remove_vendor_from_rfq(
    rfq_id: UUID,
    rfq_vendor_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    rfq = db.query(RequestForQuotation).filter(
        RequestForQuotation.id == rfq_id,
        RequestForQuotation.company_id == user.company_id
    ).first()

    if not rfq:
        raise HTTPException(404, "RFQ not found")

    if rfq.status not in ("DRAFT", "SENT"):
        raise HTTPException(400, "Cannot remove vendor at this stage")

    vendor_link = db.query(RequestForQuotationVendor).filter(
        RequestForQuotationVendor.id == rfq_vendor_id,
        RequestForQuotationVendor.rfq_id == rfq_id
    ).first()

    if not vendor_link:
        raise HTTPException(404, "Vendor not linked to RFQ")

    db.delete(vendor_link)
    db.commit()

    return {"message": "Vendor removed from RFQ"}





@router.post("/{rfq_id}/send-email")
async def send_rfq_emails(
    rfq_id: UUID,
    vendor_ids: list[UUID],
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # 🔹 1. Get RFQ
    rfq = db.query(RequestForQuotation).filter(
        RequestForQuotation.id == rfq_id,
        RequestForQuotation.company_id == user.company_id
    ).first()

    if not rfq:
        raise HTTPException(404, "RFQ not found")

    # 🔹 2. Get PR attachments
    
    attachments = db.query(RequestForQuotationAttachment).filter(
        RequestForQuotationAttachment.rfq_id == rfq_id
    ).all()

    

    # 🔹 Build absolute file paths
    BASE_DIR = "D:/ERP_AI_JCPL_backend/backend"  # 🔥 put your actual backend root

    file_paths = []

    for att in attachments:
        clean_path = att.file_path.replace("\\", "/")
        full_path = os.path.join(BASE_DIR,"uploads", clean_path)

        if os.path.exists(full_path):
            file_paths.append(full_path)

    
    # 🔹 3. Get vendors
    vendors = db.query(Vendor).filter(
        Vendor.id.in_(vendor_ids),
        Vendor.company_id == user.company_id
    ).all()

    # 🔹 4. Send emails
    for vendor in vendors:
        if not vendor.email:
            continue  # skip if no email

        await send_rfq_email(
            email=vendor.email,
            file_paths=file_paths,
            vendor_name=vendor.name
        )

    return {"message": "Emails sent successfully"}


@router.get("/{rfq_id}/vendor/{rfq_vendor_id}/quotation")
def get_vendor_quotation_api(
    rfq_id: UUID,
    rfq_vendor_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return get_vendor_quotation(db, rfq_id, rfq_vendor_id, user)