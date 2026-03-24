from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from decimal import Decimal


class POManualItem(BaseModel):
    material_name: str
    description: Optional[str] = None
    specification: Optional[str] = None   # ✅ NEW

    quantity: Decimal
    unit_id: UUID
    unit_name: Optional[str] = None       # ✅ NEW
    rate: Decimal
    hsn_code: Optional[str] = None
    weight: Optional[Decimal] = None


from typing import Optional
from uuid import UUID

class POManualCreate(BaseModel):
    vendor_id: UUID

    # ✅ VENDOR SNAPSHOT
    vendor_address_line1: Optional[str] = None
    vendor_address_line2: Optional[str] = None
    vendor_contact: Optional[str] = None

    # ✅ HEADER
    plot_no: Optional[str] = None
    po_date: Optional[str] = None   # (optional override)

    # ✅ FACTORY
    factory_id: Optional[UUID] = None
    factory_range: Optional[str] = None
    factory_division: Optional[str] = None
    factory_commissionerate: Optional[str] = None
    factory_gstin: Optional[str] = None

    # ✅ TERMS
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    transporter: Optional[str] = None
    freight_paid: Optional[bool] = True
    other_instructions: Optional[str] = None

    # ✅ TAX
    sgst_percent: Decimal
    cgst_percent: Decimal

    items: List[POManualItem]