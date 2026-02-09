from datetime import date
from sqlalchemy.orm import Session
from app.models.purchase.pr_number_sequence import PRNumberSequence


def get_financial_year(today: date | None = None) -> str:
    today = today or date.today()
    year = today.year
    if today.month < 4:
        return f"{year-1}-{str(year)[-2:]}"
    return f"{year}-{str(year+1)[-2:]}"


def generate_pr_number(db: Session, company_id) -> str:
    fy = get_financial_year()

    seq = (
        db.query(PRNumberSequence)
        .filter(
            PRNumberSequence.company_id == company_id,
            PRNumberSequence.financial_year == fy
        )
        .with_for_update()
        .first()
    )

    if not seq:
        seq = PRNumberSequence(
            company_id=company_id,
            financial_year=fy,
            last_number=1
        )
        db.add(seq)
        pr_no = 1
    else:
        seq.last_number += 1
        pr_no = seq.last_number

    return f"PR/{fy}/{pr_no:06d}"
