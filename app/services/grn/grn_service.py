import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal

from app.models.grn.grn import GRN, GRNStatus
from app.models.grn.grn_item import GRNItem
from app.models.grn.stock_movement import StockMovement, StockMovementType

from app.models.purchase.purchase_order import PurchaseOrder
from app.models.purchase.purchase_order import PurchaseOrderItem
FULL_ACCESS_ROLES = ["admin", "superadmin", "manager"]

# ============================================
# HELPER: Generate GRN Number
# ============================================
def generate_grn_number():
    return f"GRN-{uuid.uuid4().hex[:8].upper()}"


# ============================================
# CREATE GRN (DRAFT)
# ============================================
def create_grn_draft(db: Session, data, user):
    # 1. Fetch PO
    po = db.query(PurchaseOrder).filter(
        PurchaseOrder.id == data.po_id,
        PurchaseOrder.company_id == user.company_id
    ).first()

    

    

    if not po:
        raise Exception("PO not found")
    
    if user.role.lower() not in FULL_ACCESS_ROLES:
        if po.factory_id not in user.factory_ids:
            raise Exception("You are not allowed to create GRN for this factory")
        
    # 2. Create GRN
    grn = GRN(
        grn_number=generate_grn_number(),
        company_id=user.company_id,
        po_id=po.id,
        vendor_id=po.vendor_id,
        factory_id=data.factory_id,
        status=GRNStatus.DRAFT,
        remarks=data.remarks,
        created_by=user.id
    )

    db.add(grn)
    db.flush()

    # 3. Add Items
    for item in data.items:

        po_item = db.query(PurchaseOrderItem).filter(
            PurchaseOrderItem.id == item.po_item_id
        ).first()
        
        grn_item = GRNItem(
            grn_id=grn.id,
            po_item_id=item.po_item_id,
            material_id = (
                item.material_id
                if item.material_id
                else po_item.material_id
            ),
            unit_id = (
                item.unit_id
                if item.unit_id
                else po_item.unit_id   # 🔥 fallback
            ),
            ordered_qty=item.ordered_qty,
            received_qty=item.received_qty,
            accepted_qty=item.received_qty,
            rejected_qty=item.rejected_qty,
            batch_number=item.batch_number,
            barcode=item.barcode
        )
        db.add(grn_item)

    db.commit()
    db.refresh(grn)

    return grn


# ============================================
# HELPER: Get Total Received Qty (per PO item)
# ============================================
def get_total_received_qty(db, po_item_id, exclude_grn_id=None):
    query = db.query(
        func.coalesce(func.sum(GRNItem.received_qty), 0)
    ).join(GRN).filter(
        GRNItem.po_item_id == po_item_id,
        GRN.status == GRNStatus.SUBMITTED
    )

    if exclude_grn_id:
        query = query.filter(GRN.id != exclude_grn_id)

    result = query.scalar()

    return Decimal(result or 0)


# ============================================
# SUBMIT GRN
# ============================================
def submit_grn(db: Session, grn_id, user):
    grn = db.query(GRN).filter(
        GRN.id == grn_id,
        GRN.company_id == user.company_id
    ).first()

    if not grn:
        raise Exception("GRN not found")

    if grn.status != GRNStatus.DRAFT:
        raise Exception("Only draft GRN can be submitted")
    
    if user.role.lower() not in FULL_ACCESS_ROLES:
        if grn.factory_id not in user.factory_ids:
            raise Exception("Not allowed for this factory")

    for item in grn.items:

        # 1. Validate qty consistency
        if item.received_qty != (item.accepted_qty + item.rejected_qty):
            raise Exception("Received qty must equal accepted + rejected")

        # 2. Fetch PO Item
        po_item = db.query(PurchaseOrderItem).filter(
            PurchaseOrderItem.id == item.po_item_id
        ).first()

        if not po_item:
            raise Exception("PO item not found")

        # 3. Calculate already received qty
        total_received = get_total_received_qty(db, item.po_item_id, exclude_grn_id=grn.id)

        # 4. Prevent over-receipt
        if total_received + item.received_qty > po_item.quantity:
            raise Exception("Over receipt not allowed")

        # 5. STOCK MOVEMENT (ONLY ACCEPTED QTY)
        if item.accepted_qty > 0:

            po_item = db.query(PurchaseOrderItem).filter(
                PurchaseOrderItem.id == item.po_item_id
            ).first()

            material_name = (
                item.material.material_name
                if item.material
                else po_item.material_name
            )

            stock = StockMovement(
                company_id=grn.company_id,
                material_id = (
                    item.material_id
                    if item.material_id
                    else po_item.material_id
                ),
                material_name=material_name,
                factory_id=grn.factory_id,
                movement_type=StockMovementType.GRN,
                quantity=item.accepted_qty,
               unit_id = (
                    item.unit_id
                    if item.unit_id
                    else po_item.unit_id   # 🔥 fallback
                ),
                reference_id=grn.id,
                reference_type="GRN"
            )

            db.add(stock)

    # 6. Update GRN status
    grn.status = GRNStatus.SUBMITTED

    db.commit()
    db.refresh(grn)

    return grn

def update_grn(db: Session, grn_id, data, user):
    grn = db.query(GRN).filter(
        GRN.id == grn_id,
        GRN.company_id == user.company_id
    ).first()

    

    if not grn:
        raise Exception("GRN not found")

    # ❌ Cannot edit cancelled
    if grn.status == GRNStatus.CANCELLED:
        raise Exception("Cannot edit cancelled GRN")
    
    if user.role.lower() not in FULL_ACCESS_ROLES:
        if grn.factory_id not in user.factory_ids:
            raise Exception("Not allowed for this factory")

    # ===============================
    # 🔥 STEP 1: IF SUBMITTED → REVERSE STOCK ONCE
    # ===============================
    if grn.status == GRNStatus.SUBMITTED:

        for item in grn.items:

            po_item = db.query(PurchaseOrderItem).filter(
                PurchaseOrderItem.id == item.po_item_id
            ).first()

            if item.accepted_qty > 0:
                db.add(StockMovement(
                    company_id=grn.company_id,
                    material_id = (
                        item.material_id
                        if item.material_id
                        else po_item.material_id
                    ),
                    material_name=(
                        item.material.material_name
                        if item.material
                        else None
                    ),
                    factory_id=grn.factory_id,
                    movement_type=StockMovementType.ADJUSTMENT,
                    quantity=-1 * item.accepted_qty,
                    unit_id = (
                        item.unit_id
                        if item.unit_id
                        else po_item.unit_id   # 🔥 fallback
                    ),
                    reference_id=grn.id,
                    reference_type="GRN_EDIT_REVERSAL"
                ))

        # 👉 VERY IMPORTANT
        grn.status = GRNStatus.DRAFT

    # ===============================
    # 🔥 STEP 2: UPDATE HEADER
    # ===============================
    grn.factory_id = data.factory_id
    grn.remarks = data.remarks

    # ===============================
    # 🔥 STEP 3: REPLACE ITEMS (SAFE NOW)
    # ===============================
    db.query(GRNItem).filter(GRNItem.grn_id == grn.id).delete()

    for item in data.items:

        po_item = db.query(PurchaseOrderItem).filter(
            PurchaseOrderItem.id == item.po_item_id
        ).first()

        db.add(GRNItem(
            grn_id=grn.id,
            po_item_id=item.po_item_id,
            material_id = (
                item.material_id
                if item.material_id
                else po_item.material_id
            ),
            unit_id = item.unit_id if item.unit_id else po_item.unit_id,
            ordered_qty=item.ordered_qty,
            received_qty=item.received_qty,
            accepted_qty=item.received_qty,
            rejected_qty=item.rejected_qty,
            batch_number=item.batch_number,
            barcode=item.barcode
        ))

    db.commit()
    db.refresh(grn)

    return grn

def cancel_grn(db: Session, grn_id, user):
    grn = db.query(GRN).filter(
        GRN.id == grn_id,
        GRN.company_id == user.company_id
    ).first()

    if not grn:
        raise Exception("GRN not found")

    if grn.status == GRNStatus.CANCELLED:
        raise Exception("GRN already cancelled")
    
    if user.role.lower() not in FULL_ACCESS_ROLES:
        if grn.factory_id not in user.factory_ids:
            raise Exception("Not allowed for this factory")

    # If already submitted → reverse stock
    if grn.status == GRNStatus.SUBMITTED:
        for item in grn.items:
            reverse_stock = StockMovement(
                company_id=grn.company_id,
                material_id=item.material_id,
                factory_id=grn.factory_id,
                movement_type=StockMovementType.ADJUSTMENT,
                quantity= -1 * item.accepted_qty,  # reverse
                unit_id=item.unit_id,
                reference_id=grn.id,
                reference_type="GRN_CANCEL"
            )
            db.add(reverse_stock)

    grn.status = GRNStatus.CANCELLED

    db.commit()
    db.refresh(grn)

    return grn