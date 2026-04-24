from app.models.purchase.purchase_order import PurchaseOrder
from app.models.vendor import Vendor
from uuid import UUID
from sqlalchemy.orm import joinedload

FULL_ACCESS_ROLES = ["admin", "superadmin", "manager"]

def get_po_list(db, user, status=None, page=1, limit=10000, factory_id=None):

    query = db.query(PurchaseOrder, Vendor).options(
        joinedload(PurchaseOrder.factory)
    ).join(
        Vendor, Vendor.id == PurchaseOrder.vendor_id
    ).filter(
        PurchaseOrder.company_id == user.company_id
    )

    

    # 🔥 DROPDOWN FILTER
    

    if factory_id:
        factory_uuid = UUID(factory_id)
        query = query.filter(PurchaseOrder.factory_id == factory_uuid)
        
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
            "po_date": po.po_date.isoformat() if po.po_date else None,
            "plot_no": po.plot_no,   # ✅ ADD THIS
            "vendor_id": po.vendor_id,
            "vendor_name": vendor.name,
            "factory_name": po.factory.name if po.factory else None,
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