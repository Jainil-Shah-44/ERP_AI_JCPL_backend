from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

# Updated imports to match your project's structure
from app.db.session import get_db
from app.api.deps import get_current_user

# Import all service functions
from app.services.dashboard.dashboard_service import (
    get_pr_dashboard_stats,
    get_po_dashboard_stats,
    get_grn_dashboard_stats
)

# 1. Define the prefix exactly like you do in purchase-requisition.py
router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)

# 2. The endpoint is now just "/pr-stats" because the prefix handles the rest.
# 3. Changed to a standard `def` (instead of async) to match your other routes, 
#    and added the `get_current_user` dependency so it isn't blocked by auth middleware.
@router.get("/pr-stats")
def get_pr_stats(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # The router is now clean and only handles the HTTP request/response routing
    return get_pr_dashboard_stats(db, user)


@router.get("/po-stats")
def get_po_stats(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return get_po_dashboard_stats(db, user)   

@router.get("/grn-stats")
def get_grn_stats(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_grn_dashboard_stats(db, user)     