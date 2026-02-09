from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.purchase.request_for_quotation import RFQCreate
from app.services.purchase.request_for_quotation_service import create_rfq_from_pr

router = APIRouter(prefix="/rfq", tags=["RFQ"])


@router.post("/")
def create_rfq(
    payload: RFQCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        return create_rfq_from_pr(db, payload, user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
