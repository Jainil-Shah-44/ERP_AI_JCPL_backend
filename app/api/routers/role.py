from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.role import Role

router = APIRouter(
    prefix="/api/roles",
    tags=["Roles"]
)

@router.get("/")
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).all()

    return [
        {
            "id": str(r.id),
            "name": r.name
        }
        for r in roles
    ]