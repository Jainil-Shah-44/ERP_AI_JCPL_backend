from typing import Optional
from uuid import UUID
from app.schemas.base import MasterReadBase, ORMBase

class UnitCreate(ORMBase):
    unit_code: str
    description: Optional[str] = None
    base_unit_id: Optional[UUID] = None
    conversion_factor: Optional[float] = None

class UnitUpdate(ORMBase):
    unit_code: Optional[str] = None
    description: Optional[str] = None
    base_unit_id: Optional[UUID] = None
    conversion_factor: Optional[float] = None
    is_active: Optional[bool] = None

class UnitRead(MasterReadBase):
    unit_code: str
    description: Optional[str]
    base_unit_id: Optional[UUID]
    conversion_factor: Optional[float]
