from agents.ingestion_graph import source_routing_graph
from core.database import SessionLocal


db = SessionLocal()

try:
    initial_state = {
        "db": db,
        "source_type": "web",
        "source": "https://en.wikipedia.org/wiki/Rohit_Sharma",
        "is_valid": False,
        "success": False,
        "title": "",
        "raw_text": "",
        "source_url": None,
        "metadata": {},
        "analysis_result": {},
        "cleaned_text_length": 0,
        "document_type": "",
        "document_type_confidence": 0.0,
        "document_id": None,
        "saved_to_db": False,
        "error": None
    }

    result = source_routing_graph.invoke(
        initial_state
    )

    print("SUCCESS:")
    print(result["success"])

    print("\nIS VALID:")
    print(result["is_valid"])

    print("\nTITLE:")
    print(result["title"])

    print("\nSOURCE URL:")
    print(result["source_url"])

    print("\nRAW TEXT LENGTH:")
    print(len(result["raw_text"]))

    print("\nCLEANED TEXT LENGTH:")
    print(result["cleaned_text_length"])

    print("\nDOCUMENT TYPE:")
    print(result["document_type"])

    print("\nDOCUMENT TYPE CONFIDENCE:")
    print(result["document_type_confidence"])

    print("\nSAVED TO DB:")
    print(result["saved_to_db"])

    print("\nDOCUMENT ID:")
    print(result["document_id"])

    print("\nERROR:")
    print(result["error"])

finally:
    db.close()



