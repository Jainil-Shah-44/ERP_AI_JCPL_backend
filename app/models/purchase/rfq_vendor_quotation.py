import uuid
from sqlalchemy import Column, Numeric, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base


class RFQVendorQuotation(Base):
    __tablename__ = "rfq_vendor_quotation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    rfq_id = Column(UUID(as_uuid=True), nullable=False)
    rfq_vendor_id = Column(UUID(as_uuid=True), nullable=False)
    rfq_item_id = Column(UUID(as_uuid=True), nullable=False)

    quoted_rate = Column(Numeric(14,2), nullable=False)
    quoted_amount = Column(Numeric(16,2), nullable=False)

    lead_time_days = Column(Integer)
    remarks = Column(Text)

    created_at = Column(DateTime, server_default=func.now())
