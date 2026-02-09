from uuid import UUID
from pydantic import BaseModel


class RFQItemQuotation(BaseModel):
    rfq_item_id: UUID
    quoted_rate: float
    lead_time_days: int | None = None
    remarks: str | None = None


class RFQVendorQuotationCreate(BaseModel):
    rfq_vendor_id: UUID
    items: list[RFQItemQuotation]
