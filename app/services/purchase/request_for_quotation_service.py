from sqlalchemy.orm import Session
from app.models.purchase.purchase_requisition import PurchaseRequisition, PurchaseRequisitionItem
from app.models.purchase.request_for_quotation import RequestForQuotation
from app.models.purchase.request_for_quotation_item import RequestForQuotationItem
from app.services.purchase.rfq_number_service import generate_rfq_number


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

    rfq = RequestForQuotation(
        company_id=user.company_id,
        company_code=user.company_code,
        rfq_number=rfq_number,
        source_pr_id=pr.id,
        remarks=payload.remarks,
        created_by=user.id
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
                quantity=item.approved_qty or item.requested_qty,
                unit_id=item.unit_id                
            )
        )

    db.commit()
    db.refresh(rfq)

    return {
        "rfq_id": rfq.id,
        "rfq_number": rfq.rfq_number,
        "status": rfq.status
    }
