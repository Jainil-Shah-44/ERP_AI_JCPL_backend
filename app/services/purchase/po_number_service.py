from datetime import date
from sqlalchemy.orm import Session
from app.models.purchase.po_number_sequence import PONumberSequence


def get_financial_year(today: date | None = None) -> str:
    today = today or date.today()
    year = today.year
    if today.month < 4:
        return f"{year-1}-{str(year)[-2:]}"
    return f"{year}-{str(year+1)[-2:]}"


def generate_po_number(db: Session, company_id):
    fy = get_financial_year()

    seq = (
        db.query(PONumberSequence)
        .filter(
            PONumberSequence.company_id == company_id,
            PONumberSequence.financial_year == fy
        )
        .with_for_update()
        .first()
    )

    if not seq:
        seq = PONumberSequence(
            company_id=company_id,
            financial_year=fy,
            last_number=1
        )
        db.add(seq)
        po_no = 1
    else:
        seq.last_number += 1
        po_no = seq.last_number

    return f"PO/{fy}/{po_no:06d}"
