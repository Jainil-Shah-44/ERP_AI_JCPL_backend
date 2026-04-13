import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship




class GRNStatus:
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    CANCELLED = "CANCELLED"


class GRN(Base):
    __tablename__ = "grn"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    

    grn_number = Column(String, unique=True, nullable=False)

    company_id = Column(UUID(as_uuid=True), nullable=False)

    po_id = Column(UUID(as_uuid=True), ForeignKey("purchase_order.id"), nullable=False)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendor.id"), nullable=False)

    factory_id = Column(UUID(as_uuid=True), ForeignKey("factory.id"), nullable=False)

    status = Column(
        Enum(
            GRNStatus.DRAFT,
            GRNStatus.SUBMITTED,
            GRNStatus.CANCELLED,
            name="grn_status_enum"
        ),
        default=GRNStatus.DRAFT,
        nullable=False
    )

    remarks = Column(Text, nullable=True)

    created_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    items = relationship(
        "GRNItem",
        back_populates="grn",
        cascade="all, delete-orphan"
    )

    po = relationship("PurchaseOrder")
    vendor = relationship("Vendor")
    factory = relationship("Factory")
    