from typing import TypedDict, Any
from types import SimpleNamespace
from langgraph.graph import StateGraph, START, END

from services.nlp_analysis_service import NLPAnalysisService
from ingestion.ingestion_router import ingest
from repositories.document_repository import DocumentRepository

class IngestionGraphState(TypedDict):
    db: Any
    source_type: str
    source: str
    is_valid: bool
    success: bool
    title: str
    raw_text: str
    source_url: str | None
    metadata: dict
    analysis_result: dict
    cleaned_text_length: int
    document_type: str
    document_type_confidence: float
    document_id: int | None
    saved_to_db: bool
    error: str | None

def validate_input(state: IngestionGraphState)  -> IngestionGraphState:

    source_type=state['source_type']
    source=state['source']    

    if not source or not source_type:

        state['is_valid'] = False
        state["success"] = False
        state["error"] = "source_type and source are required."

        return state

    allowed_source_types = {
        "web",
        "pdf",
        "youtube",
        "ocr",
        "github"
    }

    if source_type not in allowed_source_types:

        state["is_valid"] = False
        state["success"] = False
        state["error"] = f"Unsupported source_type: {source_type}"
        return state

    state["is_valid"] = True
    state["error"] = None

    return state

def route_after_validation(
    state: IngestionGraphState
) ->str:

    if state["is_valid"]:
        return "continue"

    return "stop"

def run_ingestion(
    state: IngestionGraphState
) -> IngestionGraphState:

    try:
        ingestion_result = ingest(
            source_type=state["source_type"],
            source=state["source"]
        )

        state["success"] = True
        state["title"] = ingestion_result.title
        state["raw_text"] = ingestion_result.raw_text
        state["source_url"] = ingestion_result.source_url
        state["metadata"] = ingestion_result.metadata or {}
        state["error"] = None

        return state

    except Exception as error:
        state["success"] = False
        state["error"] = str(error)
        return state

def run_nlp_analysis(
    state: IngestionGraphState
) -> IngestionGraphState:

    try:
        ingestion_result = SimpleNamespace(
            title=state["title"],
            source_type=state["source_type"],
            source_url=state["source_url"],
            raw_text=state["raw_text"],
            metadata=state["metadata"]
        )

        nlp_service = NLPAnalysisService()

        analysis_result = nlp_service.analyse_document(
            ingestion_result=ingestion_result,
            max_summary_sentences=5
        )

        transformer_analysis = (
            analysis_result
            .get("analysis", {})
            .get("metadata", {})
            .get("transformer_analysis", {})
        )

        state["analysis_result"] = analysis_result
        state["cleaned_text_length"] = analysis_result["text"]["cleaned_text_length"]
        state["document_type"] = transformer_analysis.get("document_type", "unknown")
        state["document_type_confidence"] = transformer_analysis.get("confidence", 0.0)
        state["success"] = True
        state["error"] = None

        return state

    except Exception as error:
        state["success"] = False
        state["error"] = str(error)
        return state

def save_document_to_db(
    state: IngestionGraphState
) -> IngestionGraphState:

    try:
        document_repository = DocumentRepository()

        analysis_result = state["analysis_result"]

        saved_document = document_repository.create_document(
            db=state["db"],
            title=analysis_result["title"],
            source_type=analysis_result["source_type"],
            source_url=analysis_result["source_url"],
            raw_text=state["raw_text"],
            cleaned_text=analysis_result["text"]["cleaned_text"],
            cleaned_text_preview=analysis_result["text"]["preview"],
            nlp_metadata=analysis_result["analysis"]
        )

        state["document_id"] = saved_document.document_id
        state["saved_to_db"] = True
        state["success"] = True
        state["error"] = None

        return state

    except Exception as error:
        state["saved_to_db"] = False
        state["success"] = False
        state["error"] = str(error)
        return state

def build_ingestion_graph():

    graph= StateGraph(IngestionGraphState)

    graph.add_node(
        "validate_input",
        validate_input
    )

    graph.add_node(
        "run_ingestion",
        run_ingestion
    )

    graph.add_node(
        "run_nlp_analysis",
        run_nlp_analysis
    )

    graph.add_edge(
        START,
        "validate_input"
    )

    graph.add_node(
        "save_document_to_db",
        save_document_to_db
    )

    graph.add_conditional_edges(
        "validate_input",
        route_after_validation,
        {
            "continue": "run_ingestion",
            "stop": END
        }
    )

    graph.add_edge(
        "run_ingestion",
        "run_nlp_analysis"
    )

    graph.add_edge(
        "run_nlp_analysis",
        "save_document_to_db"
    )

    graph.add_edge(
        "save_document_to_db",
        END
    )
    
    return graph.compile()

source_routing_graph = build_ingestion_graph()
