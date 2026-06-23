from sqlalchemy.orm import Session

from models.document import Document
from schemas.ingestion import IngestionOutput

def create_document(
    db: Session,
    document: IngestionOutput
):

    db_document = Document(
        title=document.title,
        source_type=document.source_type,
        source_url=document.source_url,
        raw_text=document.raw_text,
        metadata_json=document.metadata
    )

    db.add(db_document)

    db.commit()

    db.refresh(db_document)

    return db_document

