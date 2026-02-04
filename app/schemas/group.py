from typing import Optional
from app.schemas.base import MasterReadBase, ORMBase

class GroupCreate(ORMBase):
    name: str
    description: Optional[str] = None

class GroupUpdate(ORMBase):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class GroupRead(MasterReadBase):
    name: str
    description: Optional[str]
