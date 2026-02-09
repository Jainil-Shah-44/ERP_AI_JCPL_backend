from sqlalchemy.orm import Session
from app.models.purchase.purchase_requisition import (
    PurchaseRequisition,
    PurchaseRequisitionItem
)
from app.services.purchase.pr_number_service import generate_pr_number


def create_pr(db: Session, payload, user):

    if not payload.items:
        raise ValueError("PR must contain at least one item")

    # 👇 company context comes from user
    company_id = user.company_id
    company_code = user.company_code

    pr_number = generate_pr_number(db, company_id)

    pr = PurchaseRequisition(
        company_id=company_id,
        company_code=company_code,
        pr_number=pr_number,
        requested_by=user.id,
        department=payload.department,
        factory_id=payload.factory_id,
        warehouse_id=payload.warehouse_id,
        priority=payload.priority,
        required_by_date=payload.required_by_date,
        remarks=payload.remarks,
        created_by=user.id
    )

    db.add(pr)
    db.flush()

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
                estimated_amount=(
                    item.requested_qty * item.estimated_rate
                    if item.estimated_rate else None
                )
            )
        )

    db.commit()
    db.refresh(pr)

    return {
        "id": pr.id,
        "pr_number": pr.pr_number,
        "status": pr.status
    }
