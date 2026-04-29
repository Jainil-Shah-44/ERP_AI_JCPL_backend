from app.models.purchase.request_for_quotation import RequestForQuotation
from app.models.purchase.purchase_requisition import PurchaseRequisition
from sqlalchemy.orm import joinedload

def get_rfq_list(db, user, status=None, page=1, limit=20):

    query = db.query(RequestForQuotation).join(
        PurchaseRequisition,
        RequestForQuotation.source_pr_id == PurchaseRequisition.id
    )

    if status:
        query = query.filter(RequestForQuotation.status == status)

    total = query.count()

    records = (
    query.options(joinedload(RequestForQuotation.source_pr))  # 🔥 IMPORTANT
    .order_by(RequestForQuotation.created_at.desc())
    .offset((page - 1) * limit)
    .limit(limit)
    .all()
)

    data = [
        {
            "id": rfq.id,
            "rfq_number": rfq.rfq_number,
            "rfq_date": rfq.rfq_date,
            "status": rfq.status,
            "created_at": rfq.created_at,

            # ✅ ADD THESE
            "source_pr_id": rfq.source_pr_id,
            "source_pr_number": rfq.source_pr.pr_number if rfq.source_pr else None,
        }
        for rfq in records
    ]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": data
    }
