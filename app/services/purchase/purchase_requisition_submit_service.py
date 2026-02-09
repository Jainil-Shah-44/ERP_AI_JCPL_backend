from datetime import datetime
from sqlalchemy.orm import Session
from app.models.purchase.purchase_requisition import PurchaseRequisition
from app.models.purchase.purchase_requisition_approval import PurchaseRequisitionApproval


def submit_pr(db: Session, pr_id, user):

    pr = db.query(PurchaseRequisition).filter(
        PurchaseRequisition.id == pr_id,
        PurchaseRequisition.company_id == user.company_id,
        PurchaseRequisition.is_active == True
    ).first()

    if not pr:
        raise ValueError("PR not found")

    if pr.status != "DRAFT":
        raise ValueError("Only DRAFT PR can be submitted")

    # 🔒 Lock PR
    pr.status = "SUBMITTED"

    # 🧩 Approval strategy (v1)
    # Level 1 → Factory Manager (creator's manager)
    # For now, we auto-assign to self (can be replaced by RBAC later)

    approval = PurchaseRequisitionApproval(
        pr_id=pr.id,
        level=1,
        approver_id=user.id
    )

    db.add(approval)
    db.commit()

    return {
        "pr_id": pr.id,
        "status": pr.status,
        "message": "PR submitted for approval"
    }
