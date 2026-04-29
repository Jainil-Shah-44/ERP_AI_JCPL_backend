from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.purchase.purchase_requisition import PurchaseRequisition
from app.models.purchase.purchase_order import PurchaseOrder
from app.models.grn.grn import GRN
from app.core.permissions import get_user_permissions

FULL_ACCESS_ROLES = ["admin", "superadmin", "manager"]

def get_pr_dashboard_stats(db: Session, user):
    """
    Fetches the aggregate counts of Purchase Requisitions grouped by status,
    respecting tenant isolation and user permissions.
    """
    # 1. Fetch user permissions
    permissions = get_user_permissions(db, user.id)

    # 2. Base query: Select status and count, filtered by the user's company
    query = db.query(
        PurchaseRequisition.status, 
        func.count(PurchaseRequisition.id)
    ).filter(
        PurchaseRequisition.company_id == user.company_id
    )

    # 3. Permission aware filtering
    if "PR_VIEW_ALL" in permissions:
        pass  # admin sees all counts
    elif "PR_VIEW_OWN" in permissions:
        query = query.filter(
            PurchaseRequisition.created_by == user.id
        )
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to view PR stats")

    # 4. Apply the GROUP BY clause and execute
    result = query.group_by(PurchaseRequisition.status).all()
    
    # 5. Initialize default structure for the frontend UI
    stats = {
        "DRAFT": 0,
        "SUBMITTED": 0,
        "REJECTED": 0,
        "APPROVED": 0
    }
    
    # 6. Bind the actual PostgreSQL counts to the dictionary
    for row in result:
        # row[0] is the status, row[1] is the count
        status_name = str(row[0]).upper() if row[0] else ""
        actual_count = row[1]
        
        if status_name in stats:
            stats[status_name] = actual_count
            
    return stats


def get_po_dashboard_stats(db: Session, user):
    """
    Fetches the aggregate counts of Purchase Orders grouped by status,
    respecting tenant isolation and user permissions.
    """
    # 1. Fetch user permissions
    permissions = get_user_permissions(db, user.id)

    # 2. Base query: Select status and count, filtered by the user's company
    query = db.query(
        PurchaseOrder.status, 
        func.count(PurchaseOrder.id)
    ).filter(
        PurchaseOrder.company_id == user.company_id
    )

    # # 3. Permission aware filtering
    # if "PO_VIEW_ALL" in permissions:
    #     pass  # admin sees all counts
    # elif "PO_VIEW_OWN" in permissions:
    #     query = query.filter(
    #         PurchaseOrder.created_by == user.id
    #     )
    # else:
    #     raise HTTPException(status_code=403, detail="You do not have permission to view PO stats")

    # 4. Apply the GROUP BY clause and execute
    result = query.group_by(PurchaseOrder.status).all()
    
    # 5. Initialize default structure matching the frontend POStatsCard expectations
    stats = {
        "ALL": 0,
        "DRAFT": 0,
        "RELEASED": 0,
        "CANCELLED": 0
    }
    
    # 6. Bind the actual PostgreSQL counts to the dictionary
    for row in result:
        status_name = str(row[0]).upper() if row[0] else ""
        actual_count = row[1]
        
        # Add to the "ALL" aggregate total
        stats["ALL"] += actual_count
        
        # Bind to the specific status key if it exists in our dictionary
        if status_name in stats and status_name != "ALL":
            stats[status_name] = actual_count
            
    return stats


def get_grn_dashboard_stats(db: Session, user):
    """
    Fetches the aggregate counts of Goods Receipt Notes grouped by status,
    respecting tenant isolation and user permissions.
    """
    # 1. Fetch user permissions
    permissions = get_user_permissions(db, user.id)

    # 2. Base query: Select status and count, filtered by the user's company
    query = db.query(
        GRN.status, 
        func.count(GRN.id)
    ).filter(
        GRN.company_id == user.company_id
    )

    # # 3. Permission aware filtering
    # if "GRN_VIEW_ALL" in permissions:
    #     pass  # admin sees all counts
    # elif "GRN_VIEW_OWN" in permissions:
    #     query = query.filter(
    #         GRN.created_by == user.id
    #     )
    # else:
    #     raise HTTPException(status_code=403, detail="You do not have permission to view GRN stats")

    # 4. Apply the GROUP BY clause and execute

    if user.role.lower() not in FULL_ACCESS_ROLES:
        query = query.filter(GRN.factory_id.in_(user.factory_ids))

    result = query.group_by(GRN.status).all()
    
    # 5. Initialize default structure matching the frontend GRNStatsCard expectations
    stats = {
        "DRAFT": 0,
        "SUBMITTED": 0
    }
    
    # 6. Bind the actual PostgreSQL counts to the dictionary
    for row in result:
        status_name = str(row[0]).upper() if row[0] else ""
        actual_count = row[1]
        
        # If your DB uses different names (like "RECEIVED"), map them here
        if status_name in stats:
            stats[status_name] = actual_count
            
    return stats    