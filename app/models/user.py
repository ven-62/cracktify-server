from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    email_address = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    is_engineer = Column(Boolean, default=False, nullable=False)

    # Points to another user
    assigned_engineer = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Who is my engineer?
    assigned_engineer_user = relationship(
        "User",
        remote_side=[id],
        foreign_keys=[assigned_engineer],
    )

    # Which users are assigned to me?
    assigned_users = relationship(
        "User",
        foreign_keys=[assigned_engineer],
    )