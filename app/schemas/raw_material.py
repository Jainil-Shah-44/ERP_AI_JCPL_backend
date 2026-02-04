from typing import Optional
from uuid import UUID
from app.schemas.base import MasterReadBase, ORMBase

class RawMaterialCreate(ORMBase):
    material_code: str
    material_name: str
    description: Optional[str] = None
    category_id: UUID
    group_id: UUID
    unit_id: UUID

class RawMaterialUpdate(ORMBase):
    material_code: Optional[str] = None
    material_name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    group_id: Optional[UUID] = None
    unit_id: Optional[UUID] = None
    is_active: Optional[bool] = None

class RawMaterialRead(MasterReadBase):
    material_code: str
    material_name: str
    description: Optional[str]
    category_id: UUID
    group_id: UUID
    unit_id: UUID
