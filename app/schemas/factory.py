from typing import Optional
from app.schemas.base import MasterReadBase, ORMBase

class FactoryCreate(ORMBase):
    name: str
    description: Optional[str] = None
    coordinates: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    address3: Optional[str] = None
    incharge_name: Optional[str] = None
    mobile_number: Optional[str] = None
    email: Optional[str] = None

class FactoryUpdate(ORMBase):
    name: Optional[str] = None
    description: Optional[str] = None
    coordinates: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    address3: Optional[str] = None
    incharge_name: Optional[str] = None
    mobile_number: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

class FactoryRead(MasterReadBase):
    name: str
    description: Optional[str]
    coordinates: Optional[str]
    address1: Optional[str]
    address2: Optional[str]
    address3: Optional[str]
    incharge_name: Optional[str]
    mobile_number: Optional[str]
    email: Optional[str]
