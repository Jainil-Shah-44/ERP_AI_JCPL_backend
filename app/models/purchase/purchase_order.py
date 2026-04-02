import uuid
from sqlalchemy import Column, String, Date, Numeric, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base


class PurchaseOrder(Base):
    __tablename__ = "purchase_order"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    company_id = Column(UUID(as_uuid=True), nullable=False)
    company_code = Column(String(20), nullable=False)

    po_number = Column(String(30), nullable=False, unique=True)
    po_date = Column(Date, server_default=func.current_date(), nullable=False)

    vendor_id = Column(UUID(as_uuid=True), nullable=False)

    source_rfq_id = Column(UUID(as_uuid=True), nullable=True)

    status = Column(String(20), default="DRAFT")
    # DRAFT | RELEASED | CLOSED | CANCELLED

    total_amount = Column(Numeric(16, 2))


    vendor_address = Column(String)
    vendor_contact = Column(String)

    # NEW FIELDS

    plot_no = Column(String(100))

    vendor_address_line1 = Column(String)
    vendor_address_line2 = Column(String)

    factory_id = Column(UUID(as_uuid=True))    

    factory_range = Column(String)
    factory_division = Column(String)
    factory_commissionerate = Column(String)
    factory_gstin = Column(String)

    delivery_terms = Column(String)
    payment_terms = Column(String)

    transporter = Column(String)
    freight_paid = Column(Boolean, default=True)

    other_instructions = Column(String)

    sgst_percent = Column(Numeric(5, 2))
    cgst_percent = Column(Numeric(5, 2))

    sgst_amount = Column(Numeric(16, 2))
    cgst_amount = Column(Numeric(16, 2))

    # 🔷 TAX TYPE (NEW)
    tax_type = Column(String(10))  # "GST" or "IGST"

    # 🔷 IGST (NEW)
    igst_percent = Column(Numeric(5, 2), default=0)
    igst_amount = Column(Numeric(16, 2), default=0)

    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_item"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    po_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    rfq_item_id = Column(UUID(as_uuid=True), nullable=True)

    material_id = Column(UUID(as_uuid=True), nullable=True)
    material_code = Column(String(50))
    material_name = Column(String(255))

    quantity = Column(Numeric(14, 3), nullable=False)
    unit_id = Column(UUID(as_uuid=True), nullable=False)

    rate = Column(Numeric(14, 2), nullable=False)
    amount = Column(Numeric(16, 2), nullable=False)


    description = Column(String)
    specification = Column(String)
    unit_name = Column(String(50))
    hsn_code = Column(String(20))
    weight = Column(Numeric(10, 3))

    lead_time_days = Column(String(10))
