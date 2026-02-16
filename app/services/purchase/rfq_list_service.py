from app.models.purchase.request_for_quotation import RequestForQuotation


def get_rfq_list(db, user, status=None, page=1, limit=20):

    query = db.query(RequestForQuotation).filter(
        RequestForQuotation.company_id == user.company_id
    )

    if status:
        query = query.filter(RequestForQuotation.status == status)

    total = query.count()

    records = (
        query.order_by(RequestForQuotation.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    data = [
        {
            "id": rfq.id,
            "rfq_number": rfq.rfq_number,
            "rfq_date": rfq.rfq_date,
            "status": rfq.status,
            "created_at": rfq.created_at
        }
        for rfq in records
    ]

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "data": data
    }
