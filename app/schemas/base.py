from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class ORMBase(BaseModel):
    class Config:
        from_attributes = True

class MasterReadBase(ORMBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
