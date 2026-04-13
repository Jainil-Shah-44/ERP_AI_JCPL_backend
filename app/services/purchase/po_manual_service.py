from sqlalchemy.orm import Session
from decimal import Decimal
from app.models.purchase.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.vendor import Vendor
from app.models.factory import Factory
from app.models.unit import Unit
from app.services.purchase.po_number_service import generate_po_number


def create_manual_po(db: Session, payload, user):

    try:
        # 🔍 Vendor validation
        vendor = db.query(Vendor).filter(
            Vendor.id == payload.vendor_id
        ).first()

        if not vendor:
            raise ValueError("Vendor not found")

        # 🔍 Factory (optional)
        factory = None
        if payload.factory_id:
            factory = db.query(Factory).filter(
                Factory.id == payload.factory_id
            ).first()

        # 🔢 Generate PO number
        po_number = generate_po_number(db, user.company_id)

        # 🧾 Vendor snapshot (IMPORTANT)
        vendor_address_line1 = payload.vendor_address_line1 or getattr(vendor, "address_line2", "") or ""
        vendor_address_line2 = payload.vendor_address_line2 or getattr(vendor, "address_line3", "") or ""

        vendor_contact = payload.vendor_contact or getattr(vendor, "contact_number", "") or ""

        # 🧾 Factory snapshot (IMPORTANT)
        factory_range = payload.factory_range or (factory.range if factory else "")
        factory_division = payload.factory_division or (factory.division if factory else "")
        factory_commissionerate = payload.factory_commissionerate or (factory.commissionerate if factory else "")
        factory_gstin = payload.factory_gstin or (factory.gstin if factory else "")

        # 🧾 Create PO
        po = PurchaseOrder(
            company_id=user.company_id,
            company_code=user.company_code,
            po_number=po_number,
            vendor_id=vendor.id,
            created_by=user.id,

            # 🔷 Vendor snapshot
            vendor_address_line1=vendor_address_line1,
            vendor_address_line2=vendor_address_line2,
            vendor_contact=vendor_contact,
            po_date=payload.po_date,

            # 🔷 Header
            plot_no=payload.plot_no,

            # 🔷 Factory snapshot
            factory_id=payload.factory_id,
            factory_range=factory_range,
            factory_division=factory_division,
            factory_commissionerate=factory_commissionerate,
            factory_gstin=factory_gstin,

            # 🔷 Terms
            payment_terms=payload.payment_terms,
            delivery_terms=payload.delivery_terms,
            transporter=payload.transporter,
            freight_paid=payload.freight_paid,
            other_instructions=payload.other_instructions,

            # 🔷 Tax
            sgst_percent=payload.sgst_percent,
            cgst_percent=payload.cgst_percent,
        )

        db.add(po)
        db.flush()

        # 💰 Totals
        total = Decimal("0.00")

        unit_ids = [item.unit_id for item in payload.items if item.unit_id]

        units = db.query(Unit).filter(Unit.id.in_(unit_ids)).all()
        unit_map = {u.id: u.unit_code for u in units}

        for item in payload.items:

            if item.quantity <= 0:
                raise ValueError("Quantity must be greater than 0")

            if item.rate <= 0:
                raise ValueError("Rate must be greater than 0")

            amount = (item.quantity * item.rate).quantize(Decimal("0.01"))
            total += amount

            # 🔍 Unit name fetch (fallback)
            unit_name = item.unit_name or unit_map.get(item.unit_id, "")
            if not unit_name:
                unit = db.query(Unit).filter(Unit.id == item.unit_id).first()
                unit_name = unit.unit_code if unit else ""

            db.add(PurchaseOrderItem(
                po_id=po.id,

                rfq_item_id=None,
                material_id=item.material_id,

                material_name=item.material_name,
                description=item.description,
                specification=item.specification,

                quantity=item.quantity,
                unit_id=item.unit_id,
                unit_name=unit_name,

                rate=item.rate,
                amount=amount,

                hsn_code=item.hsn_code,
                weight=item.weight
            ))

        # 🧾 Tax calculation (NEW)

        po.tax_type = payload.tax_type

        if payload.tax_type == "IGST":
            igst_amount = (total * payload.igst_percent / Decimal("100")).quantize(Decimal("0.01"))

            po.igst_percent = payload.igst_percent
            po.igst_amount = igst_amount

            po.sgst_percent = Decimal("0")
            po.cgst_percent = Decimal("0")
            po.sgst_amount = Decimal("0")
            po.cgst_amount = Decimal("0")

            po.total_amount = (total + igst_amount).quantize(Decimal("0.01"))

        else:  # GST
            sgst_amount = (total * payload.sgst_percent / Decimal("100")).quantize(Decimal("0.01"))
            cgst_amount = (total * payload.cgst_percent / Decimal("100")).quantize(Decimal("0.01"))

            po.sgst_percent = payload.sgst_percent
            po.cgst_percent = payload.cgst_percent
            po.sgst_amount = sgst_amount
            po.cgst_amount = cgst_amount

            po.igst_percent = Decimal("0")
            po.igst_amount = Decimal("0")

            po.total_amount = (total + sgst_amount + cgst_amount).quantize(Decimal("0.01"))
        db.commit()

        return {
            "po_id": po.id,
            "po_number": po.po_number
        }

    except Exception as e:
        db.rollback()
        raise e