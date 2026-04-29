from sqlalchemy.orm import Session
from app.models.purchase.request_for_quotation import RequestForQuotation
from app.models.purchase.request_for_quotation_vendor import RequestForQuotationVendor


def invite_vendors_to_rfq(db: Session, rfq_id, vendor_ids, user):

    rfq = db.query(RequestForQuotation).filter(
        RequestForQuotation.id == rfq_id,
        RequestForQuotation.company_id == user.company_id
    ).first()

    if not rfq:
        raise ValueError("RFQ not found")

    if rfq.status in ("CLOSED", "CANCELLED"):
        raise ValueError("Cannot invite vendors for closed RFQ")

    # 🔥 FETCH EXISTING VENDORS
    existing_vendor_ids = {
        v.vendor_id
        for v in db.query(RequestForQuotationVendor)
        .filter(RequestForQuotationVendor.rfq_id == rfq.id)
        .all()
    }

    added_count = 0

    for vendor_id in vendor_ids:
        if vendor_id in existing_vendor_ids:
            continue  # ✅ SKIP duplicates

        db.add(
            RequestForQuotationVendor(
                rfq_id=rfq.id,
                vendor_id=vendor_id
            )
        )
        added_count += 1

    if rfq.status == "DRAFT":
        rfq.status = "SENT"

    db.commit()

    return {
        "rfq_id": rfq.id,
        "status": rfq.status,
        "vendors_invited": added_count
    }