from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    mobile_number: Optional[str] = None
    role: str
    location: Optional[str] = None
    password: str
    factory_ids: Optional[List[UUID]] = []

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile_number: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None
    factory_ids: Optional[List[UUID]] = []
class UserRead(BaseModel):
    id: UUID
    username: str
    email: Optional[str]
    mobile_number: Optional[str]
    role: Optional[str]
    location: Optional[str]
    company_code: str
    is_active: bool
    factory_ids: Optional[List[UUID]] = []

    class Config:
        from_attributes = True
