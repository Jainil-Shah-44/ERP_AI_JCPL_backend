from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import MasterBase

class Warehouse(MasterBase):
    __tablename__ = "warehouse"

    company_id = Column(ForeignKey("company.id"), nullable=False)
    name = Column(String, nullable=False)
    location = Column(String)
    state = Column(String)
    pincode = Column(String)
    incharge = Column(String)

    company = relationship("Company")
