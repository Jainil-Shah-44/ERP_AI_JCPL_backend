from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.purchase.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.vendor import Vendor
from app.services.purchase.po_number_service import generate_po_number


def create_manual_po(db: Session, payload, user):

    # 🔍 Vendor validation
    vendor = db.query(Vendor).filter(
        Vendor.id == payload.vendor_id
    ).first()

    if not vendor:
        raise ValueError("Vendor not found")

    # 🔢 Generate PO number
    po_number = generate_po_number(db, user.company_id)

    # 🧾 Create PO header
    po = PurchaseOrder(
        company_id=user.company_id,
        company_code=user.company_code,
        po_number=po_number,
        vendor_id=vendor.id,
        created_by=user.id,

        vendor_address=payload.vendor_address or getattr(vendor, "address", None) or "N/A",
        vendor_contact=payload.vendor_contact or getattr(vendor, "contact_number", None) or "N/A",

        payment_terms=payload.payment_terms,
        delivery_terms=payload.delivery_terms,
        transporter=payload.transporter,
        freight_paid=payload.freight_paid,
        other_instructions=payload.other_instructions,

        sgst_percent=payload.sgst_percent,
        cgst_percent=payload.cgst_percent,
    )

    db.add(po)
    db.flush()

    # 💰 Calculate totals
    total = Decimal("0.00")

    for item in payload.items:

        if item.quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

        if item.rate <= 0:
            raise ValueError("Rate must be greater than 0")

        amount = item.quantity * item.rate
        total += amount

        db.add(PurchaseOrderItem(
            po_id=po.id,

            # RFQ fields null
            rfq_item_id=None,
            material_id=None,

            material_name=item.material_name,
            description=item.description,

            quantity=item.quantity,
            unit_id=item.unit_id,
            rate=item.rate,
            amount=amount,

            hsn_code=item.hsn_code,
            weight=item.weight
        ))

    # 🧾 Tax calculation
    sgst_amount = (total * payload.sgst_percent) / Decimal("100")
    cgst_amount = (total * payload.cgst_percent) / Decimal("100")

    po.sgst_amount = sgst_amount
    po.cgst_amount = cgst_amount
    po.total_amount = total + sgst_amount + cgst_amount

    db.commit()

    return {
        "po_id": po.id,
        "po_number": po.po_number
    }