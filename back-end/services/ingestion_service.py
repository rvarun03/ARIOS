from sqlalchemy.orm import Session

from ingestion.web_ingestor import ingest_web
from ingestion.pdf_ingestor import ingest_pdf
from ingestion.youtube_ingestor import ingest_youtube
from ingestion.ocr_ingestor import ingest_image
from ingestion.github_ingestor import ingest_github

from repositories.document_repository import (
    create_document
)


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

    document = create_document(
        db=db,
        document=output
    )

    return document