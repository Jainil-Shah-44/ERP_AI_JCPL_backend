from collections import defaultdict
from sqlalchemy.orm import Session
from decimal import Decimal


from app.models.purchase.request_for_quotation import RequestForQuotation
from app.models.purchase.request_for_quotation_item import RequestForQuotationItem
from app.models.purchase.request_for_quotation_vendor import RequestForQuotationVendor
from app.models.purchase.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.services.purchase.po_number_service import generate_po_number


def create_po_from_rfq_selection(db: Session, payload, user):

    rfq = db.query(RequestForQuotation).filter(
        RequestForQuotation.id == payload.rfq_id,
        RequestForQuotation.company_id == user.company_id
    ).first()

    if not rfq:
        raise ValueError("RFQ not found")

    if rfq.status not in ("QUOTATION_RECEIVED", "SENT"):
        raise ValueError("RFQ is not ready for PO creation")

    # 🔁 Group selections by vendor
    selections_by_vendor = defaultdict(list)

    for sel in payload.selections:
        selections_by_vendor[sel.rfq_vendor_id].append(sel)

    created_pos = []

    for rfq_vendor_id, selections in selections_by_vendor.items():

        rfq_vendor = db.query(RequestForQuotationVendor).filter(
            RequestForQuotationVendor.id == rfq_vendor_id
        ).first()

        if not rfq_vendor:
            raise ValueError("Invalid RFQ vendor selected")

        po_number = generate_po_number(db, user.company_id)

        po = PurchaseOrder(
            company_id=user.company_id,
            company_code=user.company_code,
            po_number=po_number,
            vendor_id=rfq_vendor.vendor_id,
            source_rfq_id=rfq.id,
            created_by=user.id
        )

        db.add(po)
        db.flush()

        total_amount = 0

        for sel in selections:
            rfq_item = db.query(RequestForQuotationItem).filter(
                RequestForQuotationItem.id == sel.rfq_item_id,
                RequestForQuotationItem.rfq_id == rfq.id
            ).first()

            if not rfq_item:
                raise ValueError("Invalid RFQ item")

            rate = Decimal(sel.final_rate)
            amount = rfq_item.quantity * rate
            total_amount += amount

            db.add(
                PurchaseOrderItem(
                    po_id=po.id,
                    rfq_item_id=rfq_item.id,
                    material_id=rfq_item.material_id,
                    material_code=rfq_item.material_code,
                    material_name=rfq_item.material_name,
                    quantity=rfq_item.quantity,
                    unit_id=rfq_item.unit_id,                    
                    rate=rate,
                    amount=amount,
                    lead_time_days=sel.lead_time_days
                )
            )

        po.total_amount = total_amount
        created_pos.append({
            "po_id": po.id,
            "po_number": po.po_number,
            "vendor_id": po.vendor_id,
            "total_amount": float(total_amount)
        })

    rfq.status = "CLOSED"
    db.commit()

    return {
        "rfq_id": rfq.id,
        "purchase_orders": created_pos
    }
