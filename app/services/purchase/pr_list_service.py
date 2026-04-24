from sqlalchemy.orm import Session
from app.models.purchase.purchase_requisition import PurchaseRequisition
from app.core.permissions import get_user_permissions


def get_pr_list(db: Session, user, status=None, page=1, limit=10000):

    permissions = get_user_permissions(db, user.id)

    query = db.query(PurchaseRequisition).filter(
        PurchaseRequisition.company_id == user.company_id
    )

    # -----------------------------
    # Permission aware filtering
    # -----------------------------
    if "PR_VIEW_ALL" in permissions:
        pass  # admin sees all

    elif "PR_VIEW_OWN" in permissions:
        query = query.filter(
            PurchaseRequisition.created_by == user.id
        )

    else:
        raise Exception("You do not have permission to view PR")

    if status:
        query = query.filter(PurchaseRequisition.status == status)

    total = query.count()

    records = (
        query.order_by(PurchaseRequisition.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    data = [
        {
            "id": pr.id,
            "pr_number": pr.pr_number,
            "department": pr.department,
            "priority": pr.priority,
            "status": pr.status,
            "created_at": pr.created_at
        }
        for pr in records
    ]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": data
    }