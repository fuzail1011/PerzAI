from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base
from sqlalchemy import func
from pgvector.sqlalchemy import Vector

import uuid

Base = declarative_base()


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    doc_id = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        nullable=False,
        index=True,
    )
    document_name = Column(
        String,
        nullable=False,
    )
    user_id = Column(
        Integer,
        nullable=False,
    )
    persona_id = Column(
        Integer,
        nullable=False,
    )
    chunk_text = Column(
        Text,
        nullable=False,
    )
    embedding = Column(
        Vector(1536),
        nullable=False,
    )
    _metadata = Column(
        "metadata",
        JSONB,
        nullable=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
