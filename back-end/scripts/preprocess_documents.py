import json
from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]

sys.path.append(str(BACKEND_DIR))

from core.paths import RAW_DIR, OUTPUT_FILE
from ingestion.ingestion_router import ingest


def write_jsonl(
    records: list[dict],
    output_file: Path
) -> None:

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_file.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                )
                + "\n"
            )

def collect_web_sources()->list[dict]:

    sources=[]

    urls_file = RAW_DIR / "web" / "urls.txt"

    if not urls_file.exists():
        return sources
    
    with urls_file.open("r", encoding="utf-8") as file:

        urls=[
            line.strip()
            for line in file.readlines()
            if line.strip()
        ]

        for url in urls:

            sources.append(
                {
                    "source_type": "web",
                    "source":url
                }
            )
    
    return sources     

def collect_pdf_sources()-> list[dict]:

    sources=[]

    pdf_dir= RAW_DIR/"pdfs"

    if not pdf_dir.exists():
        return sources

    for pdf_file in sorted(pdf_dir.glob("*.pdf")):

        sources.append(
            {
                "source_type": "pdf",
                "source": str(pdf_file)
            }
        )       

    return sources

def collect_image_sources() -> list[dict]:

    sources = []

    image_dir = RAW_DIR / "images"

    if not image_dir.exists():
        return sources

    allowed_extensions = [
        "*.png",
        "*.jpg",
        "*.jpeg",
        "*.webp"
    ]

    for extension in allowed_extensions:
        for image_file in sorted(image_dir.glob(extension)):
            sources.append(
                {
                    "source_type": "image",
                    "source": str(image_file)
                }
            )

    return sources        

def main() -> None:

    sources = []

    sources.extend(
        collect_web_sources()
    )

    sources.extend(
        collect_pdf_sources()
    )

    sources.extend(
        collect_image_sources()
    )

    documents = []

    for index, source_info in enumerate(sources):

        source_type = source_info["source_type"]
        source = source_info["source"]

        print(
            f"Processing {source_type}: {source}"
        )

        try:
            result = ingest(
                source_type=source_type,
                source=source
            )

        except Exception as error:
            print(
                f"Failed to process {source}: {error}"
            )
            continue

        documents.append(
            {
                "dataset_document_id": f"doc_{index + 1}",
                "title": result.title or Path(source).name,
                "source_type": result.source_type,
                "source_url": result.source_url,
                "source": source,
                "raw_text": result.raw_text or "",
                "metadata": result.metadata or {}
            }
        )    

    write_jsonl(
        records=documents,
        output_file=OUTPUT_FILE
    )

    print(
        f"Saved {len(documents)} processed documents to {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
    
