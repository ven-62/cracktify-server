from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.database.db import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    crack_id = Column(Integer, ForeignKey("cracks.id"), nullable=True)

    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    inviter_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", back_populates="notifications")
    crack = relationship("Crack", back_populates="notifications")
    inviter = relationship("User", foreign_keys=[inviter_id])

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "crack_id": self.crack_id,
            "message": self.message,
            "is_read": self.is_read,
            "inviter_id": self.inviter_id,
            "created_at": self.created_at.isoformat(),
        }
