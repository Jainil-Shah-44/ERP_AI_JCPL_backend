from uuid import UUID
from pydantic import BaseModel
from typing import List
from decimal import Decimal


class POItemSelection(BaseModel):
    rfq_item_id: UUID
    rfq_vendor_id: UUID
    final_rate: Decimal
    lead_time_days: int | None = None


class POFromRFQCreate(BaseModel):
    rfq_id: UUID
    selections: List[POItemSelection]
