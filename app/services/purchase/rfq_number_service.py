from datetime import date
from sqlalchemy.orm import Session
from app.models.purchase.rfq_number_sequence import RFQNumberSequence


def get_financial_year(today: date | None = None) -> str:
    today = today or date.today()
    year = today.year
    return f"{year-1}-{str(year)[-2:]}" if today.month < 4 else f"{year}-{str(year+1)[-2:]}"


def generate_rfq_number(db: Session, company_id):
    fy = get_financial_year()

    seq = (
        db.query(RFQNumberSequence)
        .filter(
            RFQNumberSequence.company_id == company_id,
            RFQNumberSequence.financial_year == fy
        )
        .with_for_update()
        .first()
    )

    if not seq:
        seq = RFQNumberSequence(
            company_id=company_id,
            financial_year=fy,
            last_number=1
        )
        db.add(seq)
        rfq_no = 1
    else:
        seq.last_number += 1
        rfq_no = seq.last_number

    return f"RFQ/{fy}/{rfq_no:06d}"
