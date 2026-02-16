from uuid import UUID
from pydantic import BaseModel
from typing import List
from decimal import Decimal


class PRItemUpdate(BaseModel):
    material_id: UUID
    material_code: str
    material_name: str
    requested_qty: Decimal
    unit_id: UUID
    estimated_rate: Decimal | None = None


class PRUpdate(BaseModel):
    department: str
    priority: str
    required_by_date: str
    remarks: str | None = None
    items: List[PRItemUpdate]
