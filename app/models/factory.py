from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import MasterBase

class Factory(MasterBase):
    __tablename__ = "factory"

    company_id = Column(ForeignKey("company.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    coordinates = Column(String)
    address1 = Column(String)
    address2 = Column(String)
    address3 = Column(String)
    incharge_name = Column(String)
    mobile_number = Column(String)
    email = Column(String)

    company = relationship("Company")
