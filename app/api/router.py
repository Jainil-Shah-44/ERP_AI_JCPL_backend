from fastapi import APIRouter
from app.api.routers import (
    department,
    factory,
    category,
    group,
    unit,
    vendor,
    warehouse,
    raw_material,
    user
)
from app.api.purchase_requisition import router as pr_router

api_router = APIRouter()

api_router.include_router(department.router)
api_router.include_router(factory.router)
api_router.include_router(category.router)
api_router.include_router(group.router)
api_router.include_router(unit.router)
api_router.include_router(vendor.router)
api_router.include_router(warehouse.router)
api_router.include_router(raw_material.router)
api_router.include_router(user.router)


api_router.include_router(pr_router)