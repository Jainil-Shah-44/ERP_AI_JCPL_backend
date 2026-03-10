from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.purchase.purchase_requisition import (
    PurchaseRequisition,
    PurchaseRequisitionItem
)
from app.services.purchase.pr_number_service import generate_pr_number
from app.models.department import Department


def create_pr(db: Session, payload, user):

    if not payload.items:
        raise ValueError("PR must contain at least one item")

    # Company context
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
        remarks=payload.remarks,
        created_by=user.id
    )

    db.add(pr)
    db.flush()

    # ---------------------------------------------------
    # Preload departments for performance
    # ---------------------------------------------------

    dept_ids = [item.department_id for item in payload.items if item.department_id]

    departments = {
        d.id: d
        for d in db.query(Department)
        .filter(Department.id.in_(dept_ids))
        .all()
    }

    # ---------------------------------------------------
    # Create PR Items
    # ---------------------------------------------------

    for item in payload.items:

        department = departments.get(item.department_id)

        if not department:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid department for item {item.material_name}"
            )

        db.add(
            PurchaseRequisitionItem(
                pr_id=pr.id,
                pr_number=pr_number,

                material_id=item.material_id,
                material_code=item.material_code,
                material_name=item.material_name,

                requested_qty=item.requested_qty,
                unit_id=item.unit_id,
                estimated_rate=item.estimated_rate,

                department_id=department.id,
                department_name=department.name,

                description=item.description,
                remarks=item.remarks,

                required_by_date=item.required_by_date,

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