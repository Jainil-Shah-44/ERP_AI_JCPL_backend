from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.purchase.purchase_requisition import PurchaseRequisition
from app.models.purchase.purchase_requisition import PurchaseRequisitionItem
from app.models.department import Department


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
    pr.remarks = payload.remarks

    # ------------------------------------------
    # Remove old items
    # ------------------------------------------
    db.query(PurchaseRequisitionItem).filter(
        PurchaseRequisitionItem.pr_id == pr.id
    ).delete()

    # ------------------------------------------
    # Preload departments
    # ------------------------------------------
    dept_ids = [i.department_id for i in payload.items if i.department_id]

    departments = {
        d.id: d
        for d in db.query(Department)
        .filter(Department.id.in_(dept_ids))
        .all()
    }

    # ------------------------------------------
    # Insert new items
    # ------------------------------------------
    for item in payload.items:

        dept = departments.get(item.department_id)

        if not dept:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid department for item {item.material_name}"
            )

        db.add(
            PurchaseRequisitionItem(
                pr_id=pr.id,
                pr_number=pr.pr_number,

                material_id=item.material_id,
                material_code=item.material_code,
                material_name=item.material_name,

                requested_qty=item.requested_qty,
                unit_id=item.unit_id,
                estimated_rate=item.estimated_rate,

                department_id=dept.id,
                department_name=dept.name,

                description=item.description,
                remarks=item.remarks,

                required_by_date=item.required_by_date,

                estimated_amount=(
                    item.requested_qty * item.estimated_rate
                    if item.estimated_rate else None
                ),

                status="PENDING"
            )
        )

    db.commit()

    return {"message": "PR updated successfully"}