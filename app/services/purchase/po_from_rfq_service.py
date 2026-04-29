from collections import defaultdict
from sqlalchemy.orm import Session
from decimal import Decimal


from app.models.purchase.request_for_quotation import RequestForQuotation
from app.models.purchase.request_for_quotation_item import RequestForQuotationItem
from app.models.purchase.request_for_quotation_vendor import RequestForQuotationVendor
from app.models.purchase.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.services.purchase.po_number_service import generate_po_number
from app.models.vendor import Vendor
from app.models.factory import Factory

def create_po_from_rfq_selection(db: Session, payload, user):

    
    rfq = db.query(RequestForQuotation).filter(
        RequestForQuotation.id == payload.rfq_id,
        RequestForQuotation.company_id == user.company_id
    ).first()

    if not rfq:
        raise ValueError("RFQ not found")

    if rfq.status not in ("QUOTATION_RECEIVED", "SENT"):
        raise ValueError("RFQ is not ready for PO creation")

    # 🔁 Group selections by vendor
    selections_by_vendor = defaultdict(list)

    for sel in payload.selections:
        selections_by_vendor[sel.rfq_vendor_id].append(sel)

    created_pos = []

    for rfq_vendor_id, selections in selections_by_vendor.items():
        

        rfq_vendor = db.query(RequestForQuotationVendor).filter(
            RequestForQuotationVendor.id == rfq_vendor_id
        ).first()

        if not rfq_vendor:
            raise ValueError("Invalid RFQ vendor selected")
        
        vendor = db.query(Vendor).filter(
            Vendor.id == rfq_vendor.vendor_id
        ).first()

        factory = None
        if getattr(rfq, "factory_id", None):
            factory = db.query(Factory).filter(
                Factory.id == rfq.factory_id
            ).first()


        po_number = generate_po_number(db, user.company_id)
        print("RFQ factory:", rfq.factory_id, rfq.factory_range)
        po = PurchaseOrder(
            company_id=user.company_id,
            company_code=user.company_code,
            po_number=po_number,
            vendor_id=rfq_vendor.vendor_id,
            source_rfq_id=rfq.id,
            created_by=user.id,

            # 🔷 FACTORY SNAPSHOT (FROM RFQ)
            factory_id=rfq.factory_id,
            factory_range=rfq.factory_range or "",
            factory_division=rfq.factory_division or "",
            factory_commissionerate=rfq.factory_commissionerate or "",
            factory_gstin=rfq.factory_gstin or "",

            # 🔷 Vendor snapshot
            vendor_address_line1=getattr(vendor, "address_line2", "") or "",
            vendor_address_line2=getattr(vendor, "address_line3", "") or "",
            vendor_contact=getattr(vendor, "contact_number", "") or "",

            # # 🔷 Factory snapshot (from RFQ)
            # factory_id=getattr(rfq, "factory_id", None),
            # factory_range=getattr(factory, "range", "") if factory else "",
            # factory_division=getattr(factory, "division", "") if factory else "",
            # factory_commissionerate=getattr(factory, "commissionerate", "") if factory else "",
            # factory_gstin=getattr(factory, "gstin", "") if factory else "",

            # 🔷 Header defaults from RFQ
            payment_terms=getattr(rfq, "payment_terms", ""),
            delivery_terms=getattr(rfq, "delivery_terms", ""),
            transporter="",
            other_instructions=getattr(rfq, "remarks", ""),

            # 🔷 Tax defaults
            tax_type="GST",
            sgst_percent=Decimal("9"),
            cgst_percent=Decimal("9"),
            igst_percent=Decimal("0"),
        )

        db.add(po)
        db.flush()

        total_amount = 0

        subtotal = Decimal("0.00")

        for sel in selections:
            rfq_item = db.query(RequestForQuotationItem).filter(
                RequestForQuotationItem.id == sel.rfq_item_id,
                RequestForQuotationItem.rfq_id == rfq.id
            ).first()

            if not rfq_item:
                raise ValueError("Invalid RFQ item")

            rate = Decimal(sel.final_rate)
            amount = (rfq_item.quantity * rate).quantize(Decimal("0.01"))

            subtotal += amount

            db.add(
                PurchaseOrderItem(
                    po_id=po.id,
                    rfq_item_id=rfq_item.id,

                    material_id=rfq_item.material_id,
                    material_code=rfq_item.material_code,
                    material_name=rfq_item.material_name,

                    # 🔥 IMPORTANT FIXES
                    description=rfq_item.material_description or "",
                    specification=getattr(rfq_item, "material_specification", "") or "",
                    

                    quantity=rfq_item.quantity,
                    unit_id=rfq_item.unit_id,
                    unit_name=getattr(rfq_item, "unit_name", "") or "",

                    rate=rate,
                    amount=amount,

                    lead_time_days=sel.lead_time_days
                )
            )
        # ✅ NEW STRUCTURE
        po.subtotal = subtotal
        po.additional_charges_total = Decimal("0.00")
        po.total_amount = subtotal  # temp

        
        created_pos.append({
            "po_id": po.id,
            "po_number": po.po_number,
            "vendor_id": po.vendor_id,
            "total_amount": float(total_amount)
        })

    rfq.status = "CLOSED"
    db.commit()

    return {
        "rfq_id": rfq.id,
        "purchase_orders": created_pos
    }
