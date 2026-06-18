from ingestion.web_ingestor import ingest_web
from ingestion.pdf_ingestor import ingest_pdf
from ingestion.youtube_ingestor import ingest_youtube
from ingestion.ocr_ingestor import ingest_image
from ingestion.github_ingestor import ingest_github

def ingest(source_type: str, source: str):

    source_type = source_type.lower()

    if source_type == "web":
        return ingest_web(source)

    elif source_type == "pdf":
        return ingest_pdf(source)

    elif source_type == "youtube":
        return ingest_youtube(source)

    elif source_type == "image":
        return ingest_image(source)

    elif source_type == "github":
        return ingest_github(source)

    else:
        raise ValueError(
            f"Unsupported source type: {source_type}"
        )