import argparse

from core.database import SessionLocal
from models.document import Document
from models.document_chunk import DocumentChunk


def find_relevant_chunks(
    document_id: int,
    search_text: str,
    limit: int = 20
):
    db = SessionLocal()

    try:
        document = (
            db.query(Document)
            .filter(Document.document_id == document_id)
            .first()
        )

        if not document:
            print(f"No document found with document_id={document_id}")
            return

        print("\nDOCUMENT")
        print("--------")
        print("document_id:", document.document_id)
        print("title:", document.title)
        print("source_type:", document.source_type)

        words = [
            word.strip().lower()
            for word in search_text.split()
            if len(word.strip()) > 2
        ]

        query = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
        )

        chunks = query.order_by(DocumentChunk.chunk_index.asc()).all()

        matched_chunks = []

        for chunk in chunks:
            chunk_text_lower = chunk.chunk_text.lower()

            score = sum(
                1
                for word in words
                if word in chunk_text_lower
            )

            if score > 0:
                matched_chunks.append(
                    {
                        "chunk": chunk,
                        "score": score
                    }
                )

        matched_chunks = sorted(
            matched_chunks,
            key=lambda item: item["score"],
            reverse=True
        )

        print("\nMATCHED CHUNKS")
        print("--------------")

        for item in matched_chunks[:limit]:
            chunk = item["chunk"]

            print("\n====================================")
            print("chunk_id:", chunk.chunk_id)
            print("chunk_index:", chunk.chunk_index)
            print("match_score:", item["score"])
            print("word_count:", chunk.word_count)
            print("------------------------------------")
            print(chunk.chunk_text[:1500])

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--document-id", type=int, required=True)
    parser.add_argument("--search", type=str, required=True)
    parser.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()

    find_relevant_chunks(
        document_id=args.document_id,
        search_text=args.search,
        limit=args.limit
    )