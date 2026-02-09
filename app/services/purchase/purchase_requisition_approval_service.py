from datetime import datetime
from sqlalchemy.orm import Session
from app.models.purchase.purchase_requisition import (
    PurchaseRequisition,
    PurchaseRequisitionItem
)
from app.models.purchase.purchase_requisition_approval import PurchaseRequisitionApproval


def act_on_pr(
    db: Session,
    pr_id,
    user,
    action: str,
    remarks: str | None = None
):
    approval = db.query(PurchaseRequisitionApproval).filter(
        PurchaseRequisitionApproval.pr_id == pr_id,
        PurchaseRequisitionApproval.approver_id == user.id,
        PurchaseRequisitionApproval.status == "PENDING"
    ).first()

    if not approval:
        raise ValueError("No pending approval found for this user")

    approval.status = action
    approval.action_date = datetime.utcnow()
    approval.remarks = remarks

    pr = db.query(PurchaseRequisition).filter(
        PurchaseRequisition.id == pr_id,
        PurchaseRequisition.company_id == user.company_id
    ).first()

    if not pr:
        raise ValueError("PR not found")

    pr_items = db.query(PurchaseRequisitionItem).filter(
        PurchaseRequisitionItem.pr_id == pr.id
    ).all()

    if not pr_items:
        raise ValueError("No PR items found for this PR")

    if action == "REJECT":
        pr.status = "REJECTED"
        for item in pr_items:
            item.status = "REJECTED"

    elif action == "APPROVE":
        pr.status = "APPROVED"
        for item in pr_items:
            item.status = "APPROVED"

    db.flush()
    db.commit()

    return {
        "pr_id": pr.id,
        "status": pr.status,
        "item_count": len(pr_items)
    }
