from sqlalchemy.orm import Session
from app.models.purchase.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.vendor import Vendor


def get_po_detail(db: Session, po_id, user):

    po = (
        db.query(PurchaseOrder)
        .filter(
            PurchaseOrder.id == po_id,
            PurchaseOrder.company_id == user.company_id
        )
        .first()
    )

    if not po:
        raise ValueError("PO not found")

    vendor = db.query(Vendor).filter(
        Vendor.id == po.vendor_id
    ).first()

    items = db.query(PurchaseOrderItem).filter(
        PurchaseOrderItem.po_id == po.id
    ).all()

    return {
    "id": po.id,
    "po_number": po.po_number,
    "po_date": po.po_date,

    "vendor_id": po.vendor_id,
    "vendor_name": vendor.name if vendor else None,

    # 🔽 NEW FIELDS
    "vendor_address": po.vendor_address,
    "vendor_contact": po.vendor_contact,

    "payment_terms": po.payment_terms,
    "delivery_terms": po.delivery_terms,
    "transporter": po.transporter,
    "freight_paid": po.freight_paid,

    "other_instructions": po.other_instructions,

    "sgst_percent": float(po.sgst_percent or 0),
    "cgst_percent": float(po.cgst_percent or 0),
    "sgst_amount": float(po.sgst_amount or 0),
    "cgst_amount": float(po.cgst_amount or 0),

    "total_amount": float(po.total_amount or 0),

    "status": po.status,
    "created_at": po.created_at,
    "source_rfq_id": po.source_rfq_id,

    "items": [
        {
            "id": item.id,

            "material_id": item.material_id,
            "material_code": item.material_code,
            "material_name": item.material_name,

            "description": item.description,
            "hsn_code": item.hsn_code,
            "weight": float(item.weight or 0),

            "quantity": float(item.quantity),
            "unit_id": item.unit_id,

            "rate": float(item.rate),
            "amount": float(item.amount),

            "lead_time_days": item.lead_time_days
        }
        for item in items
    ]
}