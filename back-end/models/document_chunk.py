from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from core.database import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    chunk_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    document_id= Column(
        Integer,
        ForeignKey("documents.document_id"),
        nullable=False,
        index=True
    )

    chunk_index= Column(
        Integer,
        nullable=False
    )

    chunk_text = Column(
        Text,
        nullable=False
    )

    word_count = Column(
        Integer,
        nullable=False
    )

    char_count = Column(
        Integer,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )