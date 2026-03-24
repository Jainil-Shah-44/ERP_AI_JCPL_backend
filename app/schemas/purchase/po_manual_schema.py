from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from decimal import Decimal


class POManualItem(BaseModel):
    material_name: str
    description: Optional[str] = None
    quantity: Decimal
    unit_id: UUID
    rate: Decimal
    hsn_code: Optional[str] = None
    weight: Optional[Decimal] = None


class POManualCreate(BaseModel):
    vendor_id: UUID

    vendor_address: Optional[str] = None
    vendor_contact: Optional[str] = None

    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None

    transporter: Optional[str] = None
    freight_paid: Optional[bool] = True

    other_instructions: Optional[str] = None

    sgst_percent: Decimal
    cgst_percent: Decimal

    items: List[POManualItem]