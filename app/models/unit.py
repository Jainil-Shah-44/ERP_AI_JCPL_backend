from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import MasterBase

class Unit(MasterBase):
    __tablename__ = "unit"

    company_id = Column(ForeignKey("company.id"), nullable=False)
    unit_code = Column(String, nullable=False)
    description = Column(String)
    base_unit_id = Column(ForeignKey("unit.id"))
    conversion_factor = Column(Numeric(10, 4))

    base_unit = relationship("Unit", remote_side="Unit.id")
    company = relationship("Company")
