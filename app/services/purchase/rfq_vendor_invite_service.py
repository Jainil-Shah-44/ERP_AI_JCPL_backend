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

    if rfq.status != "DRAFT":
        raise ValueError("Vendors can only be invited when RFQ is in DRAFT")

    for vendor_id in vendor_ids:
        db.add(
            RequestForQuotationVendor(
                rfq_id=rfq.id,
                vendor_id=vendor_id
            )
        )

    rfq.status = "SENT"

    db.commit()

    return {
        "rfq_id": rfq.id,
        "status": rfq.status,
        "vendors_invited": len(vendor_ids)
    }
