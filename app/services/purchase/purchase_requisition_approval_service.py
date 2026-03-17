from datetime import datetime
from sqlalchemy.orm import Session

from app.models.purchase.purchase_requisition import (
    PurchaseRequisition,
    PurchaseRequisitionItem
)


def act_on_pr(
    db: Session,
    pr_id,
    user,
    action: str,
    remarks: str | None = None
):

    pr = db.query(PurchaseRequisition).filter(
        PurchaseRequisition.id == pr_id,
        PurchaseRequisition.company_id == user.company_id
    ).first()

    if not pr:
        raise ValueError("PR not found")

    if pr.status != "SUBMITTED":
        raise ValueError("Only submitted PR can be approved or rejected")

    pr_items = db.query(PurchaseRequisitionItem).filter(
        PurchaseRequisitionItem.pr_id == pr.id
    ).all()

    if not pr_items:
        raise ValueError("No PR items found")

    # -----------------------------
    # Apply action
    # -----------------------------
    if action == "REJECT":
        pr.status = "REJECTED"
        for item in pr_items:
            item.status = "REJECTED"

    elif action == "APPROVE":
        pr.status = "APPROVED"
        for item in pr_items:
            item.status = "APPROVED"

    # -----------------------------
    # Optional audit log (good practice)
    # -----------------------------
    pr.approved_by = user.id
    pr.approved_at = datetime.utcnow()

    db.commit()

    return {
        "pr_id": pr.id,
        "status": pr.status,
        "item_count": len(pr_items)
    }