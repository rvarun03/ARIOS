from sqlalchemy.orm import Session

from ingestion.web_ingestor import ingest_web
from ingestion.pdf_ingestor import ingest_pdf
from ingestion.youtube_ingestor import ingest_youtube
from ingestion.ocr_ingestor import ingest_image
from ingestion.github_ingestor import ingest_github

from repositories.document_repository import (
    DocumentRepository
)

document_repo = DocumentRepository()


def ingest_document_service(
    source_type: str,
    source: str,
    db: Session
):

    source_type = source_type.lower()

    if source_type == "web":
        output = ingest_web(source)

    elif source_type == "pdf":
        output = ingest_pdf(source)

    elif source_type == "youtube":
        output = ingest_youtube(source)

    elif source_type == "image":
        output = ingest_image(source)

    elif source_type == "github":
        output = ingest_github(source)

    else:
        raise ValueError(
            f"Unsupported source type: {source_type}"
        )

    content_hash = document_repo.generate_hash(
        output.raw_text
    )

    existing_document = document_repo.get_by_hash(
        db,
        content_hash
    )
    
    if existing_document:
        raise ValueError(
            f"Document already exists. ID={existing_document.id}"
        )

    document = document_repo.create_document(
        db=db,
        document=output
    )

    return document