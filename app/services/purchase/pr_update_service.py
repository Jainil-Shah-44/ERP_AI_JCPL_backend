from sqlalchemy.orm import Session
from app.models.purchase.purchase_requisition import PurchaseRequisition
from app.models.purchase.purchase_requisition import PurchaseRequisitionItem


def update_pr(db: Session, pr_id, payload, user):

    pr = db.query(PurchaseRequisition).filter(
        PurchaseRequisition.id == pr_id,
        PurchaseRequisition.company_id == user.company_id
    ).first()

    if not pr:
        raise ValueError("PR not found")

    if pr.status != "DRAFT":
        raise ValueError("Only DRAFT PR can be updated")

    pr.department = payload.department
    pr.priority = payload.priority
    pr.required_by_date = payload.required_by_date
    pr.remarks = payload.remarks

    # Remove old items
    db.query(PurchaseRequisitionItem).filter(
        PurchaseRequisitionItem.pr_id == pr.id
    ).delete()

    # Insert new items
    for item in payload.items:
        db.add(
            PurchaseRequisitionItem(
                pr_id=pr.id,
                material_id=item.material_id,
                material_code=item.material_code,
                material_name=item.material_name,
                requested_qty=item.requested_qty,
                unit_id=item.unit_id,
                estimated_rate=item.estimated_rate,
                status="PENDING"
            )
        )

    db.commit()

    return {"message": "PR updated successfully"}
