import uuid
from sqlalchemy import Column, String, Date, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_order"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    company_id = Column(UUID(as_uuid=True), nullable=False)
    company_code = Column(String(20), nullable=False)

    po_number = Column(String(30), nullable=False, unique=True)
    po_date = Column(Date, server_default=func.current_date(), nullable=False)

    vendor_id = Column(UUID(as_uuid=True), nullable=False)

    source_rfq_id = Column(UUID(as_uuid=True), nullable=False)

    status = Column(String(20), default="DRAFT")
    # DRAFT | RELEASED | CLOSED | CANCELLED

    total_amount = Column(Numeric(16, 2))

    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_item"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    po_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    rfq_item_id = Column(UUID(as_uuid=True), nullable=False)

    material_id = Column(UUID(as_uuid=True), nullable=False)
    material_code = Column(String(50))
    material_name = Column(String(255))

    quantity = Column(Numeric(14, 3), nullable=False)
    unit_id = Column(UUID(as_uuid=True), nullable=False)

    rate = Column(Numeric(14, 2), nullable=False)
    amount = Column(Numeric(16, 2), nullable=False)

    lead_time_days = Column(String(10))
