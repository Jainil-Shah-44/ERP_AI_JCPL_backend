import uuid
from sqlalchemy import Column, Float, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Numeric
from app.db.base import Base


class GRNItem(Base):
    __tablename__ = "grn_item"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    grn_id = Column(UUID(as_uuid=True), ForeignKey("grn.id"), nullable=False)
    po_item_id = Column(UUID(as_uuid=True), ForeignKey("purchase_order_item.id"), nullable=False)

    material_id = Column(
        UUID(as_uuid=True),
        ForeignKey("raw_material.id"),  # ✅ REQUIRED
        nullable=True
    )

    unit_id = Column(
        UUID(as_uuid=True),
        ForeignKey("unit.id"),  # ✅ REQUIRED
        nullable=True
    )

    ordered_qty = Column(Float, nullable=False)

    received_qty = Column(Numeric(14, 3), nullable=False)
    accepted_qty = Column(Numeric(14, 3), nullable=False)
    rejected_qty = Column(Numeric(14, 3), nullable=False)

    batch_number = Column(String, nullable=True)
    barcode = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    grn = relationship("GRN", back_populates="items")

    material = relationship("RawMaterial")
    unit = relationship("Unit")
    po_item = relationship("PurchaseOrderItem")