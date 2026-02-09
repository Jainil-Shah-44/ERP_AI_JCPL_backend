import uuid
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base


class RequestForQuotationVendor(Base):
    __tablename__ = "request_for_quotation_vendor"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    rfq_id = Column(UUID(as_uuid=True), nullable=False)
    vendor_id = Column(UUID(as_uuid=True), nullable=False)

    status = Column(String(20), default="INVITED")
    invited_at = Column(DateTime, server_default=func.now())
    responded_at = Column(DateTime)
    remarks = Column(Text)
