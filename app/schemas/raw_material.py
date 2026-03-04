from typing import Optional
from uuid import UUID
from decimal import Decimal
from app.schemas.base import MasterReadBase, ORMBase


class RawMaterialCreate(ORMBase):
    material_code: str
    material_name: str
    description: Optional[str] = None

    category_id: UUID
    group_id: UUID
    unit_id: UUID

    # ✅ NEW FIELDS
    hsn_code: Optional[str] = None
    gst_rate: Optional[Decimal] = None
    reorder_level: Optional[Decimal] = None
    minimum_order_qty: Optional[Decimal] = None


class RawMaterialUpdate(ORMBase):
    material_code: Optional[str] = None
    material_name: Optional[str] = None
    description: Optional[str] = None

    category_id: Optional[UUID] = None
    group_id: Optional[UUID] = None
    unit_id: Optional[UUID] = None

    # ✅ NEW FIELDS
    hsn_code: Optional[str] = None
    gst_rate: Optional[Decimal] = None
    reorder_level: Optional[Decimal] = None
    minimum_order_qty: Optional[Decimal] = None

    is_active: Optional[bool] = None


class RawMaterialRead(MasterReadBase):
    material_code: str
    material_name: str
    description: Optional[str]

    category_id: UUID
    group_id: UUID
    unit_id: UUID

    # ✅ NEW FIELDS
    hsn_code: Optional[str]
    gst_rate: Optional[Decimal]
    reorder_level: Optional[Decimal]
    minimum_order_qty: Optional[Decimal]