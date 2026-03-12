from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import relationship
from app.database.db import Base

class Crack(Base):
    __tablename__ = "cracks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_url = Column(Text, nullable=False)
    filename = Column(Text, nullable=False)
    probability = Column(Float)
    severity = Column(String(50))
    detected_at = Column(DateTime, default=datetime.now(timezone.utc))

    user = relationship("User", back_populates="cracks")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "file_url": self.file_url,
            "filename": self.filename,
            "probability": self.probability,
            "severity": self.severity,
            "detected_at": self.detected_at.isoformat(),
        }
