from sqlalchemy import Column, String, ForeignKey
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

    company = relationship("Company")
