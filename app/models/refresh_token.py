from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid

class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("app_user.id"))
    token = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
