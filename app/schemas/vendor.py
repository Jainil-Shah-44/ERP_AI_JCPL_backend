from typing import Optional
from app.schemas.base import MasterReadBase, ORMBase

class VendorCreate(ORMBase):
    name: str
    mobile_number1: Optional[str] = None
    mobile_number2: Optional[str] = None
    office_number: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    pan_number: Optional[str] = None
    gst_number: Optional[str] = None

class VendorUpdate(ORMBase):
    name: Optional[str] = None
    mobile_number1: Optional[str] = None
    mobile_number2: Optional[str] = None
    office_number: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    pan_number: Optional[str] = None
    gst_number: Optional[str] = None
    is_active: Optional[bool] = None

class VendorRead(MasterReadBase):
    name: str
    mobile_number1: Optional[str]
    mobile_number2: Optional[str]
    office_number: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    pan_number: Optional[str]
    gst_number: Optional[str]
