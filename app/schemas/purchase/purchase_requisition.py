from datetime import date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel


class PRItemCreate(BaseModel):
    material_id: UUID
    material_code: str
    material_name: str
    requested_qty: Decimal
    unit_id: UUID
    estimated_rate: Decimal | None = None
    required_by_date: date | None = None


class PRCreate(BaseModel):
    factory_id: UUID
    warehouse_id: UUID | None = None
    department: str | None = None
    priority: str = "NORMAL"
    #required_by_date: date | None = None
    remarks: str | None = None
    items: list[PRItemCreate]
