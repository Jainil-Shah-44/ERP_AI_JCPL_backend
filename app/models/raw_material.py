from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import MasterBase

class RawMaterial(MasterBase):
    __tablename__ = "raw_material"

    company_id = Column(ForeignKey("company.id"), nullable=False)
    material_code = Column(String, nullable=False)
    material_name = Column(String, nullable=False)
    description = Column(Text)

    category_id = Column(ForeignKey("item_category.id"), nullable=False)
    group_id = Column(ForeignKey("group_master.id"), nullable=False)
    unit_id = Column(ForeignKey("unit.id"), nullable=False)

    category = relationship("ItemCategory")
    group = relationship("ItemGroup")
    unit = relationship("Unit")
    company = relationship("Company")
