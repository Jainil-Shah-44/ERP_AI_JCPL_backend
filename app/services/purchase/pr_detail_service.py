from sqlalchemy.orm import Session
from app.models.purchase.purchase_requisition import PurchaseRequisition
from app.models.purchase.purchase_requisition import PurchaseRequisitionItem
from app.models.purchase.purchase_requisition_attachment import PurchaseRequisitionAttachment


def get_pr_detail(db: Session, pr_id, user):

    pr = db.query(PurchaseRequisition).filter(
        PurchaseRequisition.id == pr_id,
        PurchaseRequisition.company_id == user.company_id
    ).first()

    if not pr:
        raise ValueError("PR not found")

    items = db.query(PurchaseRequisitionItem).filter(
        PurchaseRequisitionItem.pr_id == pr.id
    ).all()

    attachments = db.query(PurchaseRequisitionAttachment).filter(
        PurchaseRequisitionAttachment.pr_id == pr.id
    ).all()

    return {
        "id": pr.id,
        "pr_number": pr.pr_number,
        "department": pr.department,
        "priority": pr.priority,
        "required_by_date": pr.required_by_date,
        "remarks": pr.remarks,
        "status": pr.status,
        "created_at": pr.created_at,
        "items": [
            {
                "id": i.id,
                "material_id": i.material_id,
                "material_code": i.material_code,
                "material_name": i.material_name,
                "requested_qty": float(i.requested_qty),
                "approved_qty": float(i.approved_qty or 0),
                "unit_id": i.unit_id,
                "estimated_rate": float(i.estimated_rate or 0),
                "status": i.status
            }
            for i in items
        ],
        "attachments": [
            {
                "id": a.id,
                "file_name": a.file_name,
                "file_path": a.file_path
            }
            for a in attachments
        ]
    }

def get_pr_attachments(db: Session, pr_id, user):

    pr = db.query(PurchaseRequisition).filter(
        PurchaseRequisition.id == pr_id,
        PurchaseRequisition.company_id == user.company_id
    ).first()

    if not pr:
        raise ValueError("PR not found")

    attachments = db.query(PurchaseRequisitionAttachment).filter(
        PurchaseRequisitionAttachment.pr_id == pr.id
    ).all()

    return [
        {
            "id": a.id,
            "file_name": a.file_name,
            "file_path": a.file_path
        }
        for a in attachments
    ]
