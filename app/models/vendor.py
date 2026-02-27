from sqlalchemy import Column, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.db.base import MasterBase

class Vendor(MasterBase):
    __tablename__ = "vendor"

    company_id = Column(ForeignKey("company.id"), nullable=False)
    name = Column(String, nullable=False)

    mobile_number1 = Column(String)
    mobile_number2 = Column(String)
    office_number = Column(String)
    state = Column(String)
    pincode = Column(String)
    pan_number = Column(String)
    gst_number = Column(String)

    # ✅ NEW FIELDS
    email = Column(String(255))
    website = Column(String(255))
    contact_person = Column(String(150))

    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    address_line3 = Column(String(255))

    country = Column(String(100))
    credit_limit = Column(Numeric(15, 2))
    gst_registration_type = Column(String(50))

    company = relationship("Company")
