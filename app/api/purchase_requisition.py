from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.purchase.purchase_requisition import PRCreate
from app.services.purchase.purchase_requisition_service import create_pr
from app.services.purchase.purchase_requisition_submit_service import submit_pr
from app.services.purchase.purchase_requisition_approval_service import act_on_pr
from fastapi import UploadFile, File
from app.services.purchase.purchase_requisition_attachment_service import (
    save_pr_attachment
)

router = APIRouter(
    prefix="/purchase-requisition",
    tags=["Purchase Requisition"]
)


@router.post("/", status_code=201)
def create_purchase_requisition(
    payload: PRCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return create_pr(db, payload, user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{pr_id}/submit")
def submit_purchase_requisition(
    pr_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return submit_pr(db, pr_id, user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/{pr_id}/approve")
def approve_pr(
    pr_id: UUID,
    remarks: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return act_on_pr(db, pr_id, user, "APPROVE", remarks)


@router.post("/{pr_id}/reject")
def reject_pr(
    pr_id: UUID,
    remarks: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return act_on_pr(db, pr_id, user, "REJECT", remarks)


@router.post("/{pr_id}/attachment")
def upload_pr_attachment(
    pr_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return save_pr_attachment(db, pr_id, file, user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))