from sqlalchemy.orm import Session
from app.models.purchase.purchase_order import PurchaseOrder


def release_po(db: Session, po_id, user):

    po = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == po_id,
        PurchaseOrder.company_id == user.company_id
    ).first()

    if not po:
        raise ValueError("PO not found")

    if po.status != "DRAFT":
        raise ValueError("Only DRAFT PO can be released")

    po.status = "RELEASED"

    db.commit()

    return {"message": "PO released successfully"}

def cancel_po(db: Session, po_id, user):

    po = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == po_id,
        PurchaseOrder.company_id == user.company_id
    ).first()

    if not po:
        raise ValueError("PO not found")

    if po.status in ("CLOSED", "CANCELLED"):
        raise ValueError("PO cannot be cancelled at this stage")

    po.status = "CANCELLED"

    db.commit()

    return {"message": "PO cancelled successfully"}
