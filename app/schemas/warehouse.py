from typing import Optional
from app.schemas.base import MasterReadBase, ORMBase

class WarehouseCreate(ORMBase):
    name: str
    location: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    incharge: Optional[str] = None

class WarehouseUpdate(ORMBase):
    name: Optional[str] = None
    location: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    incharge: Optional[str] = None
    is_active: Optional[bool] = None

class WarehouseRead(MasterReadBase):
    name: str
    location: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    incharge: Optional[str]
