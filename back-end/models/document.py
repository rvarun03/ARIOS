# models/document.py

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON

from core.database import Base


class Document(Base):
    __tablename__ = "documents"

    document_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        nullable=False
    )

    source_type = Column(
        String,
        nullable=False
    )

    source_url = Column(
        String,
        nullable=True
    )

    file_name = Column(
        String,
        nullable=True
    )

    file_path = Column(
        String,
        nullable=True
    )

    file_type = Column(
        String,
        nullable=True
    )

    file_size = Column(
        Integer,
        nullable=True
    )

    raw_text = Column(
        Text,
        nullable=False
    )

    cleaned_text_preview = Column(
        Text,
        nullable=True
    )

    nlp_metadata = Column(
        JSON,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )