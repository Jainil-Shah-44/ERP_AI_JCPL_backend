from sqlalchemy.orm import Session
from app.models.purchase.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.vendor import Vendor
from app.models.factory import Factory
from app.models.unit import Unit


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

    # 🔹 Vendor
    vendor = db.query(Vendor).filter(
        Vendor.id == po.vendor_id
    ).first()

    # 🔹 Factory
    factory = None
    if getattr(po, "factory_id", None):
        factory = db.query(Factory).filter(
            Factory.id == po.factory_id
        ).first()

   

    # 🔹 Items
    items = db.query(PurchaseOrderItem).filter(
        PurchaseOrderItem.po_id == po.id
    ).all()

    unit_ids = [item.unit_id for item in items if item.unit_id]

    units = db.query(Unit).filter(Unit.id.in_(unit_ids)).all()
    unit_map = {u.id: u.description for u in units}

    
    return {
        "id": po.id,
        "po_number": po.po_number,
        "po_date": po.po_date,

        # 🔹 Vendor
        "vendor_id": po.vendor_id,
        "vendor_name": vendor.name if vendor else "",
        
        "vendor_address_line1": getattr(po, "vendor_address_line1", "") or "",
        "vendor_address_line2": getattr(po, "vendor_address_line2", "") or "",

        # 🔹 Factory
        "factory_id": getattr(po, "factory_id", None),
        "factory_name": factory.name if factory else "",
        "factory_range": getattr(po, "factory_range", "") or "",
        "factory_division": getattr(po, "factory_division", "") or "",
        "factory_commissionerate": getattr(po, "factory_commissionerate", "") or "",
        "factory_gstin": getattr(po, "factory_gstin", "") or "",

        # 🔹 PO Meta
        "plot_no": getattr(po, "plot_no", "") or "",
        "payment_terms": po.payment_terms or "",
        "delivery_terms": po.delivery_terms or "",
        "transporter": po.transporter or "",
        "freight_paid": po.freight_paid,
        "other_instructions": po.other_instructions or "",

        # 🔹 Tax
        "sgst_percent": float(po.sgst_percent or 0),
        "cgst_percent": float(po.cgst_percent or 0),
        "sgst_amount": float(po.sgst_amount or 0),
        "cgst_amount": float(po.cgst_amount or 0),
        "total_amount": float(po.total_amount or 0),
        "tax_type": po.tax_type,
        "igst_percent": float(po.igst_percent or 0),
        "igst_amount": float(po.igst_amount or 0),

        # 🔹 Meta
        "status": po.status,
        "created_at": po.created_at,
        "source_rfq_id": po.source_rfq_id,

        # 🔹 Items (UI-ready)
        "items": [
            {
                "id": item.id,

                "material_id": item.material_id,
                "material_code": item.material_code,
                "material_name": item.material_name or "",

                "description": item.description or "",
                "specification": getattr(item, "specification", "") or "",
                "hsn_code": item.hsn_code or "",

                "quantity": float(item.quantity or 0),
                "unit_id": item.unit_id,

                # 🔥 IMPORTANT: add unit_name
                "unit_name": unit_map.get(item.unit_id, ""),

                "rate": float(item.rate or 0),
                "amount": float(item.amount or 0),

                "lead_time_days": item.lead_time_days or ""
            }
            for item in items
        ]
    }