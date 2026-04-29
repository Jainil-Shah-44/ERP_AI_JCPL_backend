from datetime import datetime
from sqlalchemy.orm import Session
from app.models.purchase.rfq_vendor_quotation import RFQVendorQuotation
from app.models.purchase.request_for_quotation_vendor import RequestForQuotationVendor
from app.models.purchase.request_for_quotation import RequestForQuotation
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.purchase.rfq_vendor_quotation import RFQVendorQuotation
from app.models.purchase.request_for_quotation_vendor import RequestForQuotationVendor
from app.models.purchase.request_for_quotation import RequestForQuotation


def submit_vendor_quotation(db: Session, payload, user):

    rfq_vendor = db.query(RequestForQuotationVendor).filter(
        RequestForQuotationVendor.id == payload.rfq_vendor_id
    ).first()

    if not rfq_vendor:
        raise ValueError("Invalid RFQ vendor")

    for item in payload.items:

        existing = db.query(RFQVendorQuotation).filter(
            RFQVendorQuotation.rfq_vendor_id == rfq_vendor.id,
            RFQVendorQuotation.rfq_item_id == item.rfq_item_id
        ).one_or_none()   # 🔥 IMPORTANT

        if existing:
            existing.quoted_rate = item.quoted_rate
            existing.quoted_amount = item.quoted_rate
            existing.lead_time_days = item.lead_time_days
            existing.remarks = item.remarks
        else:
            db.add(
                RFQVendorQuotation(
                    rfq_id=rfq_vendor.rfq_id,
                    rfq_vendor_id=rfq_vendor.id,
                    rfq_item_id=item.rfq_item_id,
                    quoted_rate=item.quoted_rate,
                    quoted_amount=item.quoted_rate,
                    lead_time_days=item.lead_time_days,
                    remarks=item.remarks
                )
            )
    rfq_vendor.status = "RESPONDED"
    rfq_vendor.responded_at = datetime.utcnow()

    rfq = db.query(RequestForQuotation).filter(
        RequestForQuotation.id == rfq_vendor.rfq_id
    ).first()
    rfq.status = "QUOTATION_RECEIVED"

    db.commit()

    return {
        "rfq_id": rfq.id,
        "vendor_status": rfq_vendor.status
    }

def get_vendor_quotation(db: Session, rfq_id, rfq_vendor_id, user):

    rows = db.query(RFQVendorQuotation).filter(
        RFQVendorQuotation.rfq_id == rfq_id,
        RFQVendorQuotation.rfq_vendor_id == rfq_vendor_id
    ).all()

    return [
        {
            "rfq_item_id": str(r.rfq_item_id),
            "quoted_rate": float(r.quoted_rate),
            "lead_time_days": r.lead_time_days,
            "remarks": r.remarks
        }
        for r in rows
    ]