from typing import Optional
from decimal import Decimal
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

    # ✅ NEW FIELDS
    email: Optional[str] = None
    website: Optional[str] = None
    contact_person: Optional[str] = None

    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    address_line3: Optional[str] = None

    country: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    gst_registration_type: Optional[str] = None


class VendorUpdate(ORMBase):
    name: Optional[str] = None

    mobile_number1: Optional[str] = None
    mobile_number2: Optional[str] = None
    office_number: Optional[str] = None

    state: Optional[str] = None
    pincode: Optional[str] = None

    pan_number: Optional[str] = None
    gst_number: Optional[str] = None

    # ✅ NEW FIELDS
    email: Optional[str] = None
    website: Optional[str] = None
    contact_person: Optional[str] = None

    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    address_line3: Optional[str] = None

    country: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    gst_registration_type: Optional[str] = None

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

    # ✅ NEW FIELDS
    email: Optional[str]
    website: Optional[str]
    contact_person: Optional[str]

    address_line1: Optional[str]
    address_line2: Optional[str]
    address_line3: Optional[str]

    country: Optional[str]
    credit_limit: Optional[Decimal]
    gst_registration_type: Optional[str]