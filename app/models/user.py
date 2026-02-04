from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base

class User(Base):
    __tablename__ = "app_user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    company_id = Column(UUID(as_uuid=True), ForeignKey("company.id"), nullable=False)
    company_code = Column(String, nullable=False)

    username = Column(String, nullable=False)
    email = Column(String)
    mobile_number = Column(String)

    role = Column(String, nullable=False)
    location = Column(String)

    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
