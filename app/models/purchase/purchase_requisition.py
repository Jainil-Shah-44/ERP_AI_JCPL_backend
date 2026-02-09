import uuid
from datetime import date
from sqlalchemy import (
    Column, String, Date, Text, Boolean,
    ForeignKey, Numeric, DateTime
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base


class PurchaseRequisition(Base):
    __tablename__ = "purchase_requisition"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    company_id = Column(UUID(as_uuid=True), nullable=False)
    company_code = Column(String(20), nullable=False)

    pr_number = Column(String(30), nullable=False, unique=True)
    pr_date = Column(Date, default=date.today)

    requested_by = Column(UUID(as_uuid=True), nullable=False)
    department = Column(String(100))

    factory_id = Column(UUID(as_uuid=True), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True))

    priority = Column(String(20), default="NORMAL")
    status = Column(String(30), default="DRAFT")

    required_by_date = Column(Date)
    remarks = Column(Text)

    has_attachment = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(UUID(as_uuid=True))


class PurchaseRequisitionItem(Base):
    __tablename__ = "purchase_requisition_item"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    pr_id = Column(
        UUID(as_uuid=True),
        ForeignKey("purchase_requisition.id", ondelete="CASCADE"),
        nullable=False
    )

    material_id = Column(UUID(as_uuid=True), nullable=False)
    material_code = Column(String(50))
    material_name = Column(String(255))

    requested_qty = Column(Numeric(14, 3), nullable=False)
    approved_qty = Column(Numeric(14, 3))

    unit_id = Column(UUID(as_uuid=True), nullable=False)

    estimated_rate = Column(Numeric(14, 2))
    estimated_amount = Column(Numeric(16, 2))

    status = Column(String(30), default="PENDING")
