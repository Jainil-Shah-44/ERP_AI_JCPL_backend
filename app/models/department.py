from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import MasterBase

class Department(MasterBase):
    __tablename__ = "department"

    company_id = Column(ForeignKey("company.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)

    company = relationship("Company")
