from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class UserRole(Base):
    __tablename__ = "user_role"

    user_id = Column(UUID(as_uuid=True), ForeignKey("app_user.id"), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("role.id"), primary_key=True)