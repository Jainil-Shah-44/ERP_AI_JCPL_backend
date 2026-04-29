from sqlalchemy import Column, ForeignKey, String, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class PurchaseOrderCharge(Base):
    __tablename__ = "purchase_order_charges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    po_id = Column(UUID(as_uuid=True), ForeignKey("purchase_order.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(100), nullable=False)
    amount = Column(Numeric(14, 2), default=0)

    created_at = Column(DateTime, server_default=func.now())