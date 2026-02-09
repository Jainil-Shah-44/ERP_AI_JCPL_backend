import uuid
from sqlalchemy import Column, String, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class PONumberSequence(Base):
    __tablename__ = "po_number_sequence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    company_id = Column(UUID(as_uuid=True), nullable=False)
    financial_year = Column(String(9), nullable=False)
    last_number = Column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint("company_id", "financial_year", name="uq_po_company_fy"),
    )
