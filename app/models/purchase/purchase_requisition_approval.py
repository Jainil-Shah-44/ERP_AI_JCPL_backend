import uuid
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base


class PurchaseRequisitionApproval(Base):
    __tablename__ = "purchase_requisition_approval"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    pr_id = Column(
        UUID(as_uuid=True),
        ForeignKey("purchase_requisition.id", ondelete="CASCADE"),
        nullable=False
    )

    level = Column(Integer, nullable=False)
    approver_id = Column(UUID(as_uuid=True), nullable=False)

    status = Column(String(20), default="PENDING")
    action_date = Column(DateTime)
    remarks = Column(Text)

    created_at = Column(DateTime, server_default=func.now())
