import fitz

from schemas.ingestion import IngestionOutput

def extract_pdf_text(pdf_path:str) -> str:
    doc=fitz.open(pdf_path)

    text= ""

    for page in doc:
        text += page.get_text()

    doc.close()

    return text   

def ingest_pdf(pdf_path: str) -> IngestionOutput:

    try:
        raw_text= extract_pdf_text(pdf_path)
        return IngestionOutput(
            source_type="pdf",
            source_url=pdf_path,
            title=None,
            raw_text=raw_text,
            metadata={
                "length": len(raw_text)
            }
        )
    except Exception as e:

        return IngestionOutput(
            source_type="pdf",
            source_url=pdf_path,
            title=None,
            raw_text="",
            metadata={
                "error": str(e)
            }
        )    