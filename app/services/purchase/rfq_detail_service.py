from sqlalchemy.orm import Session
from app.models.purchase.request_for_quotation import RequestForQuotation
from app.models.purchase.request_for_quotation_item import RequestForQuotationItem
from app.models.purchase.request_for_quotation_vendor import RequestForQuotationVendor


def get_rfq_detail(db: Session, rfq_id, user):

    rfq = db.query(RequestForQuotation).filter(
        RequestForQuotation.id == rfq_id,
        RequestForQuotation.company_id == user.company_id
    ).first()

    if not rfq:
        raise ValueError("RFQ not found")

    items = db.query(RequestForQuotationItem).filter(
        RequestForQuotationItem.rfq_id == rfq.id
    ).all()

    return {
        "id": rfq.id,
        "rfq_number": rfq.rfq_number,
        "rfq_date": rfq.rfq_date,
        "status": rfq.status,
        "source_pr_id": rfq.source_pr_id,
        "remarks": rfq.remarks,
        "created_at": rfq.created_at,
        "items": [
            {
                "id": item.id,
                "material_id": item.material_id,
                "material_code": item.material_code,
                "material_name": item.material_name,
                "quantity": float(item.quantity),
                "unit_id": item.unit_id
            }
            for item in items
        ]
    }




def get_rfq_vendors(db: Session, rfq_id, user):

    rfq = db.query(RequestForQuotation).filter(
        RequestForQuotation.id == rfq_id,
        RequestForQuotation.company_id == user.company_id
    ).first()

    if not rfq:
        raise ValueError("RFQ not found")

    vendors = db.query(RequestForQuotationVendor).filter(
        RequestForQuotationVendor.rfq_id == rfq.id
    ).all()

    return [
        {
            "rfq_vendor_id": v.id,
            "vendor_id": v.vendor_id,
            "status": v.status,
            "invited_at": v.invited_at,
            "responded_at": v.responded_at
        }
        for v in vendors
    ]
