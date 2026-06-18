import easyocr
from schemas.ingestion import IngestionOutput

def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from image using OCR
    """

    reader = easyocr.Reader(["en"])

    results = reader.readtext(image_path)

    raw_text = " ".join(
        result[1]
        for result in results
    )

    return raw_text

def ingest_image(image_path: str) -> IngestionOutput:

    try:

        raw_text = extract_text_from_image(image_path)

        return IngestionOutput(
            source_type="image",
            source_url=image_path,
            title=None,
            raw_text=raw_text,
            metadata={
                "length": len(raw_text)
            }
        )

    except Exception as e:

        return IngestionOutput(
            source_type="image",
            source_url=image_path,
            title=None,
            raw_text="",
            metadata={
                "error": str(e)
            }
        )