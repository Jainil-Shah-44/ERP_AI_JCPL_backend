from sqlalchemy.orm import Session
from app.models.purchase.purchase_requisition import PurchaseRequisition


def get_pr_list(db: Session, user, status=None, page=1, limit=20):

    query = db.query(PurchaseRequisition).filter(
        PurchaseRequisition.company_id == user.company_id
    )

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
            #"required_by_date": pr.required_by_date,
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
