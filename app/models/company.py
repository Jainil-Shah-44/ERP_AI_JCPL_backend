from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.base import Base

class Company(Base):
    __tablename__ = "company"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
