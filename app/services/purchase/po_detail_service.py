from sqlalchemy.orm import Session
from app.models.purchase.purchase_order import PurchaseOrder, PurchaseOrderItem


def get_po_detail(db: Session, po_id, user):

    po = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == po_id,
        PurchaseOrder.company_id == user.company_id
    ).first()

    if not po:
        raise ValueError("PO not found")

    items = db.query(PurchaseOrderItem).filter(
        PurchaseOrderItem.po_id == po.id
    ).all()

    return {
        "id": po.id,
        "po_number": po.po_number,
        "po_date": po.po_date,
        "vendor_id": po.vendor_id,
        "status": po.status,
        "total_amount": float(po.total_amount or 0),
        "created_at": po.created_at,
        "items": [
            {
                "id": item.id,
                "material_id": item.material_id,
                "material_code": item.material_code,
                "material_name": item.material_name,
                "quantity": float(item.quantity),
                "unit_id": item.unit_id,
                "rate": float(item.rate),
                "amount": float(item.amount),
                "lead_time_days": item.lead_time_days
            }
            for item in items
        ]
    }
