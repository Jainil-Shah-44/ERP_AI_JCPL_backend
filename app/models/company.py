from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base import Base

class Company(Base):
    __tablename__ = "company"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    company_code = Column(String, unique=True, nullable=False)
    company_name = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
