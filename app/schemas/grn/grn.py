from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID



# =========================
# GRN ITEM
# =========================

class GRNItemCreate(BaseModel):
    po_item_id: UUID 

    material_id: Optional[UUID] = None
    unit_id: Optional[UUID] = None

    ordered_qty: float

    received_qty: float
    accepted_qty: float
    rejected_qty: float

    batch_number: Optional[str] = None
    barcode: Optional[str] = None


# =========================
# GRN CREATE
# =========================

class GRNCreate(BaseModel):
    po_id: UUID
    factory_id: UUID
    remarks: Optional[str] = None

    items: List[GRNItemCreate]


# =========================
# RESPONSE (BASIC)
# =========================

class GRNResponse(BaseModel):
    id: UUID
    grn_number: str
    status: str

    class Config:
        from_attributes = True