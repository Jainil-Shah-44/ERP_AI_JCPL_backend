import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base


class PurchaseRequisitionAttachment(Base):
    __tablename__ = "purchase_requisition_attachment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    pr_id = Column(
        UUID(as_uuid=True),
        ForeignKey("purchase_requisition.id", ondelete="CASCADE"),
        nullable=False
    )

    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_type = Column(String(50))
    file_size = Column(BigInteger)

    uploaded_by = Column(UUID(as_uuid=True), nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())

    is_active = Column(Boolean, default=True)
