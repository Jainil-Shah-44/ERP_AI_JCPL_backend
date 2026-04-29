import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base


class RequestForQuotationAttachment(Base):
    __tablename__ = "request_for_quotation_attachment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    rfq_id = Column(
        UUID(as_uuid=True),
        ForeignKey("request_for_quotation.id", ondelete="CASCADE"),
        nullable=False
    )

    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)

    created_at = Column(DateTime, server_default=func.now())