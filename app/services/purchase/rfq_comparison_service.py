from sqlalchemy.orm import Session
from app.models.purchase.request_for_quotation_item import RequestForQuotationItem
from app.models.purchase.request_for_quotation_vendor import RequestForQuotationVendor
from app.models.purchase.rfq_vendor_quotation import RFQVendorQuotation


def get_rfq_comparison_matrix(db: Session, rfq_id, user):

    rows = (
        db.query(
            RequestForQuotationItem.id.label("rfq_item_id"),
            RequestForQuotationItem.material_id,
            RequestForQuotationItem.material_code,
            RequestForQuotationItem.material_name,
            RequestForQuotationItem.quantity,
            RequestForQuotationItem.unit_id,

            RequestForQuotationVendor.id.label("rfq_vendor_id"),
            RequestForQuotationVendor.vendor_id,

            RFQVendorQuotation.quoted_rate,
            RFQVendorQuotation.lead_time_days
        )
        .join(
            RFQVendorQuotation,
            RFQVendorQuotation.rfq_item_id == RequestForQuotationItem.id
        )
        .join(
            RequestForQuotationVendor,
            RequestForQuotationVendor.id == RFQVendorQuotation.rfq_vendor_id
        )
        .filter(RequestForQuotationItem.rfq_id == rfq_id)
        .all()
    )

    if not rows:
        return {
            "rfq_id": rfq_id,
            "items": []
        }

    # 🔁 Transform flat rows → grouped matrix
    matrix = {}

    for row in rows:
        item_id = str(row.rfq_item_id)

        if item_id not in matrix:
            matrix[item_id] = {
                "rfq_item_id": row.rfq_item_id,
                "material_id": row.material_id,
                "material_code": row.material_code,
                "material_name": row.material_name,
                "quantity": float(row.quantity),
                "unit_id": row.unit_id,
                "quotations": []
            }

        matrix[item_id]["quotations"].append({
            "rfq_vendor_id": row.rfq_vendor_id,
            "vendor_id": row.vendor_id,
            "quoted_rate": float(row.quoted_rate),
            "lead_time_days": row.lead_time_days
        })

    return {
        "rfq_id": rfq_id,
        "items": list(matrix.values())
    }
