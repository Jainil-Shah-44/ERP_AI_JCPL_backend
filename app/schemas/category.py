from typing import Optional
from app.schemas.base import MasterReadBase, ORMBase

class CategoryCreate(ORMBase):
    name: str
    description: Optional[str] = None

class CategoryUpdate(ORMBase):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class CategoryRead(MasterReadBase):
    name: str
    description: Optional[str]
