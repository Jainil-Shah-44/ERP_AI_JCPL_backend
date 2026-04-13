import uuid
from sqlalchemy import Column, Float, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class StockMovementType:
    GRN = "GRN"
    ISSUE = "ISSUE"
    ADJUSTMENT = "ADJUSTMENT"


class StockMovement(Base):
    __tablename__ = "stock_movement"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    company_id = Column(UUID(as_uuid=True), nullable=False)

    material_id = Column(UUID(as_uuid=True), ForeignKey("raw_material.id"), nullable=True)
    material_name = Column(String, nullable=True)
    factory_id = Column(UUID(as_uuid=True), ForeignKey("factory.id"), nullable=False)

    movement_type = Column(
        Enum(
            StockMovementType.GRN,
            StockMovementType.ISSUE,
            StockMovementType.ADJUSTMENT,
            name="stock_movement_type_enum"
        ),
        nullable=False
    )

    quantity = Column(Float, nullable=False)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("unit.id"), nullable=False)

    reference_id = Column(UUID(as_uuid=True), nullable=False)
    reference_type = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    material = relationship("RawMaterial")
    factory = relationship("Factory")
    unit = relationship("Unit")