from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, protected, router

app = FastAPI(title="ERP Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(protected.router)
app.include_router(router.api_router)


@app.get("/")
def health():
    return {"status": "ERP Backend Running"}
