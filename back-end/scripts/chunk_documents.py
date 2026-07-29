import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]

sys.path.append(str(BACKEND_DIR))

from core.paths import OUTPUT_FILE, CHUNK_DIRECTORY
from services.text_chunking_service import TextChunkingService

CHUNK_SIZE = 500
OVERLAP = 50


def read_jsonl(
    input_file:Path
) -> list[dict]:
    
    if not input_file.exists():
        return []
    
    records=[]

    with input_file.open("r",encoding="utf-8") as file:
        
        for line in file:
            if line.strip():
                records.append(
                    json.loads(line)
                )

    return records

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

def main():

    documents=read_jsonl(
        OUTPUT_FILE
    )

    chunking_service=TextChunkingService()

    all_chunks=[]

    for document in documents:

        chunks = chunking_service.chunk_text(
            text=document["raw_text"],
            chunk_size=CHUNK_SIZE,
            overlap=OVERLAP
        )

        for chunk in chunks:
            all_chunks.append(
                {
                    "dataset_document_id": document["dataset_document_id"],
                    "title": document["title"],
                    "source_type": document["source_type"],
                    "source_url": document["source_url"],
                    "source": document["source"],
                    "chunk_index": chunk["chunk_index"],
                    "chunk_text": chunk["chunk_text"],
                    "word_count": chunk["word_count"],
                    "char_count": chunk["char_count"]
                }
            )
    write_jsonl(
        records=all_chunks,
        output_file=CHUNK_DIRECTORY
    )   

    print(
        f"Saved {len(all_chunks)} chunks to {CHUNK_DIRECTORY}"
    )     

if __name__ == "__main__":
    main()    
