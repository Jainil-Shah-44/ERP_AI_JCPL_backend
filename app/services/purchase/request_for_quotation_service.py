from sqlalchemy.orm import Session
from app.models.purchase.purchase_requisition import PurchaseRequisition, PurchaseRequisitionItem
from app.models.purchase.request_for_quotation import RequestForQuotation
from app.models.purchase.request_for_quotation_item import RequestForQuotationItem
from app.services.purchase.rfq_number_service import generate_rfq_number
from app.models.purchase.purchase_requisition_attachment import PurchaseRequisitionAttachment
from app.models.purchase.request_for_quotation_attachment import RequestForQuotationAttachment
from app.models.factory import Factory

def create_rfq_from_pr(db: Session, payload, user):

    pr = db.query(PurchaseRequisition).filter(
        PurchaseRequisition.id == payload.pr_id,
        PurchaseRequisition.company_id == user.company_id,
        PurchaseRequisition.status == "APPROVED"
    ).first()

    if not pr:
        raise ValueError("Only APPROVED PR can be converted to RFQ")

    pr_items = db.query(PurchaseRequisitionItem).filter(
        PurchaseRequisitionItem.id.in_(payload.pr_item_ids),
        PurchaseRequisitionItem.pr_id == pr.id,
        PurchaseRequisitionItem.status == "APPROVED"
    ).all()

    if not pr_items:
        raise ValueError("No approved PR items selected")

    rfq_number = generate_rfq_number(db, user.company_id)

        # 🔹 Fetch factory from PR
    factory = None
    if getattr(pr, "factory_id", None):
        factory = db.query(Factory).filter(
            Factory.id == pr.factory_id
        ).first()

    rfq = RequestForQuotation(
        company_id=user.company_id,
        company_code=user.company_code,
        rfq_number=rfq_number,
        source_pr_id=pr.id,
        remarks=payload.remarks,
        created_by=user.id,

        # 🔥 ADD THIS BLOCK
        factory_id=pr.factory_id,
        factory_range=getattr(factory, "range_", "") if factory else "",
        factory_division=getattr(factory, "division", "") if factory else "",
        factory_commissionerate=getattr(factory, "commissionerate", "") if factory else "",
        factory_gstin=getattr(factory, "gstin", "") if factory else "",
    )

    db.add(rfq)
    db.flush()

    for item in pr_items:
        db.add(
            RequestForQuotationItem(
                rfq_id=rfq.id,
                pr_id=pr.id,
                pr_item_id=item.id,
                material_id=item.material_id,
                material_code=item.material_code,
                material_name=item.material_name,
                material_specification=item.remarks or "",        # from PR remarks
                material_description=item.description or "",      # from PR description
                quantity=item.approved_qty or item.requested_qty,
                unit_id=item.unit_id                
            )
        )

        # 🔹 Copy PR attachments → RFQ
    pr_attachments = db.query(PurchaseRequisitionAttachment).filter(
        PurchaseRequisitionAttachment.pr_id == pr.id,
        PurchaseRequisitionAttachment.is_active == True
    ).all()

    for att in pr_attachments:
        db.add(
            RequestForQuotationAttachment(
                rfq_id=rfq.id,
                file_name=att.file_name,
                file_path=att.file_path
            )
        )

    db.commit()
    db.refresh(rfq)

    return {
        "rfq_id": rfq.id,
        "rfq_number": rfq.rfq_number,
        "status": rfq.status
    }
