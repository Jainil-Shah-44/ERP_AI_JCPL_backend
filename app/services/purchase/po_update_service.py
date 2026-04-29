from sqlalchemy.orm import Session
from app.models.purchase.purchase_order import PurchaseOrder, PurchaseOrderItem
from decimal import Decimal
from app.models.purchase.purchase_order_charges import PurchaseOrderCharge
from app.models.grn.grn_item import GRNItem




def update_manual_po(db: Session, po_id, payload, user):

    po = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == po_id
    ).first()

    if not po:
        raise ValueError("PO not found")

    if po.status != "DRAFT":
        raise ValueError("Only draft PO can be edited")
    
    # 🚫 Check if PO items are already used in GRN
    linked_item = db.query(GRNItem).join(
        PurchaseOrderItem,
        GRNItem.po_item_id == PurchaseOrderItem.id
    ).filter(
        PurchaseOrderItem.po_id == po.id
    ).first()
    
        
    db.query(PurchaseOrderCharge).filter(
        PurchaseOrderCharge.po_id == po.id
    ).delete()

    # 🔹 Update header
    po.vendor_id = payload.vendor_id
    po.vendor_address_line1 = payload.vendor_address_line1 or ""
    po.vendor_address_line2 = payload.vendor_address_line2 or ""
    po.plot_no = payload.plot_no
    po.po_date = payload.po_date
    po.transporter = payload.transporter
    po.payment_terms = payload.payment_terms
    po.delivery_terms = payload.delivery_terms
    po.other_instructions = payload.other_instructions

    po.factory_id = payload.factory_id
    po.factory_range = payload.factory_range
    po.factory_division = payload.factory_division
    po.factory_commissionerate = payload.factory_commissionerate
    po.factory_gstin = payload.factory_gstin
    po.tax_type = payload.tax_type

    subtotal = Decimal("0.00")

    if linked_item:
        # 🚫 DO NOT TOUCH ITEMS (GRN exists)
        
        existing_items = db.query(PurchaseOrderItem).filter(
            PurchaseOrderItem.po_id == po.id
        ).all()

        subtotal = sum([
            Decimal(i.amount or 0)
            for i in existing_items
        ])

    else:
        # ✅ SAFE TO MODIFY ITEMS

        db.query(PurchaseOrderItem).filter(
            PurchaseOrderItem.po_id == po.id
        ).delete()

        for item in payload.items:

            material_name = (item.material_name or "").strip()

            if not material_name:
                continue

            amount = (item.quantity * item.rate).quantize(Decimal("0.01"))
            subtotal += amount
            po.subtotal = subtotal

            db.add(PurchaseOrderItem(
                po_id=po.id,
                material_id=item.material_id,
                material_name=material_name,
                description=item.description,
                specification=item.specification,
                quantity=item.quantity,
                unit_id=item.unit_id,
                unit_name=item.unit_name,
                rate=item.rate,
                amount=amount,
                hsn_code=item.hsn_code,
            ))
    
    additional_total = Decimal("0.00")

    for charge in payload.charges or []:
        amount = Decimal(charge.amount).quantize(Decimal("0.01"))

        additional_total += amount

        db.add(PurchaseOrderCharge(
            po_id=po.id,
            title=charge.title,
            amount=amount
        ))

    po.additional_charges_total = additional_total

    taxable_amount = subtotal + additional_total

    # 🔹 Recalculate tax
    if payload.tax_type == "IGST":
        igst_amount = (taxable_amount * payload.igst_percent / Decimal("100")).quantize(Decimal("0.01"))

        po.igst_percent = payload.igst_percent
        po.subtotal = subtotal
        po.igst_amount = igst_amount

        po.sgst_percent = Decimal("0")
        po.cgst_percent = Decimal("0")
        po.sgst_amount = Decimal("0")
        po.cgst_amount = Decimal("0")

        po.total_amount = (taxable_amount + igst_amount).quantize(Decimal("0.01"))

    else:
        sgst_amount = (taxable_amount * payload.sgst_percent / Decimal("100")).quantize(Decimal("0.01"))
        cgst_amount = (taxable_amount * payload.cgst_percent / Decimal("100")).quantize(Decimal("0.01"))

        po.sgst_percent = payload.sgst_percent
        po.cgst_percent = payload.cgst_percent
        po.sgst_amount = sgst_amount
        po.cgst_amount = cgst_amount

        po.igst_percent = Decimal("0")
        po.igst_amount = Decimal("0")

        po.total_amount = (taxable_amount + sgst_amount + cgst_amount).quantize(Decimal("0.01"))
    
    db.commit()

    return {"message": "PO updated successfully"}