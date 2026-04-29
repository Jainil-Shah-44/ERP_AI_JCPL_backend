from sqlalchemy.orm import Session
from app.models.purchase.request_for_quotation import RequestForQuotation
from app.models.purchase.request_for_quotation_item import RequestForQuotationItem
from app.models.purchase.request_for_quotation_vendor import RequestForQuotationVendor
from app.models.vendor import Vendor
from app.models.purchase.purchase_requisition import PurchaseRequisition
from app.models.purchase.request_for_quotation_attachment import RequestForQuotationAttachment
from app.models.factory import Factory

def get_rfq_detail(db: Session, rfq_id, user):

    rfq = (
        db.query(RequestForQuotation, PurchaseRequisition.pr_number)
        .join(PurchaseRequisition, PurchaseRequisition.id == RequestForQuotation.source_pr_id)
        .filter(
            RequestForQuotation.id == rfq_id,
            RequestForQuotation.company_id == user.company_id
        )
        .first()
    )

    if not rfq:
        raise ValueError("RFQ not found")

    rfq_obj, pr_number = rfq

    items = db.query(RequestForQuotationItem).filter(
        RequestForQuotationItem.rfq_id == rfq_obj.id
    ).all()

    attachments = db.query(RequestForQuotationAttachment).filter(
        RequestForQuotationAttachment.rfq_id == rfq_obj.id
    ).all()

    factory = None
    if rfq_obj.factory_id:
        factory = db.query(Factory).filter(
            Factory.id == rfq_obj.factory_id
        ).first()

    return {
        "id": rfq_obj.id,
        "rfq_number": rfq_obj.rfq_number,
        "rfq_date": rfq_obj.rfq_date,
        "factory_id": rfq_obj.factory_id,
        "factory_name": factory.name if factory else "",
        "factory_range": rfq_obj.factory_range,
        "factory_division": rfq_obj.factory_division,
        "factory_commissionerate": rfq_obj.factory_commissionerate,
        "factory_gstin": rfq_obj.factory_gstin,
        "status": rfq_obj.status,
        "source_pr_id": rfq_obj.source_pr_id,
        "source_pr_number": pr_number,   # ✅ ADD THIS
        "remarks": rfq_obj.remarks,
        "created_at": rfq_obj.created_at,
        "items": [
            {
                "id": item.id,
                "material_id": item.material_id,
                "material_code": item.material_code,
                "material_name": item.material_name,
                "material_specification": item.material_specification,
                "material_description": item.material_description,
                "quantity": float(item.quantity),
                "unit_id": item.unit_id
            }
            for item in items
        ],
        "attachments": [
                {
                    "id": a.id,
                    "file_name": a.file_name,
                    "file_path": a.file_path
                }
                for a in attachments
            ],
    }



def get_rfq_vendors(db: Session, rfq_id, user):

    rfq = db.query(RequestForQuotation).filter(
        RequestForQuotation.id == rfq_id,
        RequestForQuotation.company_id == user.company_id
    ).first()

    if not rfq:
        raise ValueError("RFQ not found")

    rows = (
        db.query(RequestForQuotationVendor, Vendor)
        .join(Vendor, Vendor.id == RequestForQuotationVendor.vendor_id)
        .filter(
            RequestForQuotationVendor.rfq_id == rfq.id,
            Vendor.company_id == user.company_id
        )
        .all()
    )

    return [
        {
            "rfq_vendor_id": rv.id,
            "vendor_id": rv.vendor_id,
            "vendor_name": v.name,   # ✅ FIXED
            "status": rv.status,
            "invited_at": rv.invited_at,
            "responded_at": rv.responded_at
        }
        for rv, v in rows   # ✅ unpack tuple properly
    ]