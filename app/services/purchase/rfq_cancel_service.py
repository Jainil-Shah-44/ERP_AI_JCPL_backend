from sqlalchemy.orm import Session
from app.models.purchase.request_for_quotation import RequestForQuotation


def cancel_rfq(db: Session, rfq_id, user):

    rfq = db.query(RequestForQuotation).filter(
        RequestForQuotation.id == rfq_id,
        RequestForQuotation.company_id == user.company_id
    ).first()

    if not rfq:
        raise ValueError("RFQ not found")

    if rfq.status not in ("DRAFT", "SENT"):
        raise ValueError("RFQ cannot be cancelled at this stage")

    rfq.status = "CANCELLED"

    db.commit()

    return {"message": "RFQ cancelled successfully"}
