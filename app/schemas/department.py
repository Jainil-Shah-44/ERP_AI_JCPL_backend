from typing import Optional
from app.schemas.base import MasterReadBase, ORMBase

class DepartmentCreate(ORMBase):
    name: str
    description: Optional[str] = None

class DepartmentUpdate(ORMBase):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class DepartmentRead(MasterReadBase):
    name: str
    description: Optional[str]
