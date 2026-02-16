from app.models.purchase.purchase_order import PurchaseOrder


def get_po_list(db, user, status=None, page=1, limit=20):

    query = db.query(PurchaseOrder).filter(
        PurchaseOrder.company_id == user.company_id
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
            "total_amount": po.total_amount,
            "status": po.status
        }
        for po in records
    ]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": data
    }
