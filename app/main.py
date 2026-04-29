from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, protected, router
from app.api.purchase_requisition import router as pr_router
from app.api.request_for_quotation import router as rfq_router
from app.api.purchase_order import router as po_router
from fastapi.staticfiles import StaticFiles
from app.api.routers.dashboard import router as dashboard_router

app = FastAPI(title="ERP Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://103.196.187.61"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(protected.router)
app.include_router(router.api_router)
app.include_router(pr_router)
app.include_router(rfq_router)
app.include_router(po_router)
app.include_router(dashboard_router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def health():
    return {"status": "ERP Backend Running"}
