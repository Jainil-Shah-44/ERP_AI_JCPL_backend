import uuid
from sqlalchemy import Column, String, Date, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base


class RequestForQuotationItem(Base):
    __tablename__ = "request_for_quotation_item"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    rfq_id = Column(UUID(as_uuid=True), nullable=False)

    pr_id = Column(UUID(as_uuid=True), nullable=False)
    pr_item_id = Column(UUID(as_uuid=True), nullable=False)

    material_id = Column(UUID(as_uuid=True), nullable=False)
    material_code = Column(String(50))
    material_name = Column(String(255))

    quantity = Column(Numeric(14,3), nullable=False)
    unit_id = Column(UUID(as_uuid=True), nullable=False)

    required_by_date = Column(Date)

    created_at = Column(DateTime, server_default=func.now())
