from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid

class User(Base):
    __tablename__ = "app_user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("company.id"))
    company_code = Column(String)
    username = Column(String)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)
