from sqlalchemy.orm import Session
from app.models.purchase.purchase_order import PurchaseOrder, PurchaseOrderItem
from decimal import Decimal




def update_manual_po(db: Session, po_id, payload, user):

    po = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == po_id
    ).first()

    if not po:
        raise ValueError("PO not found")

    if po.status != "DRAFT":
        raise ValueError("Only draft PO can be edited")

    # 🔹 Update header
    po.vendor_id = payload.vendor_id
    po.vendor_address_line1 = payload.vendor_address_line1 or ""
    po.vendor_address_line2 = payload.vendor_address_line2 or ""
    po.plot_no = payload.plot_no
    po.transporter = payload.transporter
    po.payment_terms = payload.payment_terms
    po.delivery_terms = payload.delivery_terms
    po.other_instructions = payload.other_instructions

    po.factory_id = payload.factory_id
    po.factory_range = payload.factory_range
    po.factory_division = payload.factory_division
    po.factory_commissionerate = payload.factory_commissionerate
    po.factory_gstin = payload.factory_gstin

    # 🔹 Delete old items
    db.query(PurchaseOrderItem).filter(
        PurchaseOrderItem.po_id == po.id
    ).delete()

    total = Decimal("0.00")

    # 🔹 Reinsert items
    for item in payload.items:

        amount = item.quantity * item.rate
        total += amount

        db.add(PurchaseOrderItem(
            po_id=po.id,
            material_name=item.material_name,
            description=item.description,
            quantity=item.quantity,
            unit_id=item.unit_id,
            rate=item.rate,
            amount=amount,
            hsn_code=item.hsn_code
        ))

    # 🔹 Recalculate tax
    sgst_amount = (total * payload.sgst_percent) / Decimal("100")
    cgst_amount = (total * payload.cgst_percent) / Decimal("100")

    po.sgst_percent = payload.sgst_percent
    po.cgst_percent = payload.cgst_percent
    po.sgst_amount = sgst_amount
    po.cgst_amount = cgst_amount
    po.total_amount = total + sgst_amount + cgst_amount

    db.commit()

    return {"message": "PO updated successfully"}