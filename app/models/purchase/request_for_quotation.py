import uuid
from sqlalchemy import Column, String, Date, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class RequestForQuotation(Base):
    __tablename__ = "request_for_quotation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    company_id = Column(UUID(as_uuid=True), nullable=False)
    company_code = Column(String(20), nullable=False)

    rfq_number = Column(String(30), nullable=False, unique=True)
    rfq_date = Column(Date, server_default=func.current_date(), nullable=False)

    source_pr_id = Column(
        UUID(as_uuid=True),
        ForeignKey("purchase_requisition.id"),  # 🔥 ADD THIS
        nullable=False
    )
    source_pr = relationship("PurchaseRequisition")

    # app/models/purchase/request_for_quotation.py

    factory_id = Column(UUID(as_uuid=True), nullable=True)
    factory_range = Column(String, nullable=True)
    factory_division = Column(String, nullable=True)
    factory_commissionerate = Column(String, nullable=True)
    factory_gstin = Column(String, nullable=True)

    status = Column(String(30), default="DRAFT")
    remarks = Column(Text)

    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    