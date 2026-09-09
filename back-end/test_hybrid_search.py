from core.database import SessionLocal
from models.document import Document
from services.document_service import DocumentService


db = SessionLocal()

try:
    document_service = DocumentService()

    document = (
        db.query(Document)
        .filter(Document.title.ilike("%Virat%"))
        .order_by(Document.created_at.desc())
        .first()
    )

    if not document:
        print("No Virat document found.")
    else:
        result = document_service.hybrid_search(
            db=db,
            question="Who are Virat Kohli's parents?",
            top_k=5,
            source_type=None,
            document_id=document.document_id
        )

        print("EXPANDED QUERIES:")
        print(result["expanded_queries"])

        print("\nRESULT COUNT:")
        print(result["result_count"])

        for item in result["results"]:
            print("\n-----------------------------")
            print("HYBRID SCORE:")
            print(item.get("hybrid_score"))

            print("\nRETRIEVAL TYPE:")
            print(item.get("retrieval_type"))

            print("\nRETRIEVAL TYPES:")
            print(item.get("retrieval_types"))

            print("\nKEYWORD SCORE:")
            print(item.get("keyword_score"))

            print("\nDISTANCE:")
            print(item.get("distance"))

            print("\nCHUNK ID:")
            print(item["metadata"]["chunk_id"])

            print("\nCHUNK INDEX:")
            print(item["metadata"]["chunk_index"])

            print("\nMATCHED SEARCH QUERIES:")
            print(item.get("matched_search_queries"))

            print("\nCHUNK TEXT:")
            print(item["chunk_text"][:2500])

finally:
    db.close()