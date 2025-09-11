from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Persona(Base):
    __tablename__ = "personas"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    name = Column(
        String,
        nullable=False,
    )
    description = Column(
        String,
        nullable=True,
    )
    system_prompt = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationship back to User
    user = relationship("User", backref="personas")

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_persona_name"),)
