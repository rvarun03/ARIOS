import json
import sys
from pathlib import Path

from core.paths import BACKEND_DIR,CHUNK_DIRECTORY,EMBED_FILE

sys.path.append(str(BACKEND_DIR))

from services.embedding_service import EmbeddingService


def read_jsonl(
    input_file: Path
) -> list[dict]:

    if not input_file.exists():
        return []

    records = []

    with input_file.open("r", encoding="utf-8") as file:
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


def main() -> None:

    chunks = read_jsonl(
        CHUNK_DIRECTORY
    )

    embedding_service = EmbeddingService()

    embedded_chunks = []

    for chunk in chunks:

        embedding = embedding_service.embed_text(
            chunk["chunk_text"]
        )

        embedded_chunks.append(
            {
                "dataset_document_id": chunk["dataset_document_id"],
                "title": chunk["title"],
                "source_type": chunk["source_type"],
                "source_url": chunk["source_url"],
                "source": chunk["source"],
                "chunk_index": chunk["chunk_index"],
                "chunk_text": chunk["chunk_text"],
                "embedding_model": "all-MiniLM-L6-v2",
                "embedding_dimension": len(embedding),
                "embedding": embedding
            }
        )

    write_jsonl(
        records=embedded_chunks,
        output_file=EMBED_FILE
    )

    print(
        f"Saved {len(embedded_chunks)} embedded chunks to {EMBED_FILE}"
    )


if __name__ == "__main__":
    main()