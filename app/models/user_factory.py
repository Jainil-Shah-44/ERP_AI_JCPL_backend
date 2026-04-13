import uuid
from sqlalchemy import Column, ForeignKey, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.base import Base


class UserFactory(Base):
    __tablename__ = "user_factory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("app_user.id"), nullable=False)
    factory_id = Column(UUID(as_uuid=True), ForeignKey("factory.id"), nullable=False)

    factory_name = Column(String, nullable=True)  # 🔥 as per your requirement

    created_at = Column(DateTime, server_default=func.now())