from app.models.purchase.purchase_order import PurchaseOrder
from app.models.vendor import Vendor


def get_po_list(db, user, status=None, page=1, limit=20):

    query = (
        db.query(PurchaseOrder, Vendor)
        .join(Vendor, Vendor.id == PurchaseOrder.vendor_id)
        .filter(PurchaseOrder.company_id == user.company_id)
    )

    if status:
        query = query.filter(PurchaseOrder.status == status)

    total = query.count()

    records = (
        query.order_by(PurchaseOrder.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    data = [
        {
            "id": po.id,
            "po_number": po.po_number,
            "po_date": po.po_date,
            "vendor_id": po.vendor_id,
            "vendor_name": vendor.name,
            "total_amount": float(po.total_amount or 0),
            "status": po.status,
            "source_rfq_id": po.source_rfq_id,
            "created_at": po.created_at
        }
        for po, vendor in records
    ]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": data
    }