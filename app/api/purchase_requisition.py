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
from app.services.purchase.pr_list_service import get_pr_list
from app.services.purchase.pr_detail_service import get_pr_detail,get_pr_attachments
from app.schemas.purchase.pr_update import PRUpdate
from app.services.purchase.pr_update_service import update_pr

from app.schemas.purchase.pr_excel_import import PRExcelImportRequest
from app.services.purchase.pr_excel_import_service import import_pr_from_excel
from app.api.dependencies.permission import require_permission

router = APIRouter(
    prefix="/api/procurement/purchase-requisition",
    tags=["Purchase Requisition"],
)

@router.post("/",dependencies=[Depends(require_permission("PR_CREATE"))], status_code=201)
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

@router.post("/{pr_id}/submit",dependencies=[Depends(require_permission("PR_SUBMIT"))])
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
    

@router.post("/{pr_id}/approve",dependencies=[Depends(require_permission("PR_APPROVE"))])
def approve_pr(
    pr_id: UUID,
    remarks: str | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return act_on_pr(db, pr_id, user, "APPROVE", remarks)


@router.post("/{pr_id}/reject",dependencies=[Depends(require_permission("PR_REJECT"))])
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
    

@router.get("/")
def list_pr(
    status: str | None = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return get_pr_list(db, user, status, page, limit)


@router.get("/{pr_id}")
def get_pr(
    pr_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return get_pr_detail(db, pr_id, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{pr_id}/attachments")
def get_attachments(
    pr_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return get_pr_attachments(db, pr_id, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{pr_id}")
def update_pr_endpoint(
    pr_id: UUID,
    payload: PRUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return update_pr(db, pr_id, payload, user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/import-excel")
def import_excel_pr(
    payload: PRExcelImportRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    pr = import_pr_from_excel(
        db,
        payload.rows,
        current_user,
        current_user.company_id,
        current_user.company_code
    )

    return {
        "message": "PR created successfully",
        "pr_id": pr.id,
        "pr_number": pr.pr_number
    }
