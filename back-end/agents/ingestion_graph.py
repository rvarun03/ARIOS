from typing import TypedDict, Any
from types import SimpleNamespace
from langgraph.graph import StateGraph, START, END

from services.nlp_analysis_service import NLPAnalysisService
from ingestion.ingestion_router import ingest
from repositories.document_repository import DocumentRepository
from services.document_service import DocumentService
from services.source_type_detector import SourceTypeDetector

class IngestionGraphState(TypedDict):
    db: Any
    source_type: str
    source: str
    is_valid: bool
    success: bool
    title: str
    raw_text: str
    source_url: str | None
    file_name: str | None
    file_path: str | None
    file_type: str | None
    file_size: int | None
    metadata: dict
    analysis_result: dict
    cleaned_text_length: int
    document_type: str
    document_type_confidence: float
    document_id: int | None
    saved_to_db: bool
    indexed: bool
    indexing_result: dict
    chunk_count: int
    stored_vector_count: int
    error: str | None

def validate_input(state: IngestionGraphState)  -> IngestionGraphState:

    source=state['source']    

    if not source :

        state['is_valid'] = False
        state["success"] = False
        state["error"] = "source_type and source are required."

        return state

    detector= SourceTypeDetector()
    detected_source_type=detector.detect(source)
    

    allowed_source_types = {
        "web",
        "pdf",
        "youtube",
        "ocr",
        "github"
    }

    if detected_source_type not in allowed_source_types:

        state["is_valid"] = False
        state["success"] = False
        
        return state

    state["source_type"] = detected_source_type
    state["is_valid"] = True
    state["success"] = True
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

        document_title = (
            analysis_result.get("title")
            or state.get("file_name")
            or state.get("title")
            or "Untitled Document"
        )
        analysis_result["title"] = document_title

        transformer_analysis = (
            analysis_result
            .get("analysis", {})
            .get("metadata", {})
            .get("transformer_analysis", {})
        )

        state["analysis_result"] = analysis_result
        state["title"] = document_title
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
            title=(
                analysis_result.get("title")
                or state.get("file_name")
                or "Untitled Document"
            ),
            source_type=analysis_result["source_type"],
            source_url=analysis_result["source_url"],
            raw_text=state["raw_text"],
            cleaned_text=analysis_result["text"]["cleaned_text"],
            cleaned_text_preview=analysis_result["text"]["preview"],
            nlp_metadata=analysis_result["analysis"],
            file_name=state.get("file_name"),
            file_path=state.get("file_path"),
            file_type=state.get("file_type"),
            file_size=state.get("file_size")
        )

        state["document_id"] = saved_document.document_id
        state["saved_to_db"] = True
        state["success"] = True
        state["error"] = None

        return state

    except Exception as error:
        state["db"].rollback()
        state["saved_to_db"] = False
        state["success"] = False
        state["error"] = str(error)
        return state

def route_after_db_save(state: IngestionGraphState) -> str:

    if state["saved_to_db"] and state["document_id"]:
        return "continue"

    return "stop"

def index_document(
    state: IngestionGraphState
)-> IngestionGraphState:
    
    if not state["document_id"]:
        state["indexed"] = False
        state["success"] = False
        state["error"] = "document_id is missing. Cannot index document."
        return state

    document_service= DocumentService()

    indexing_result= document_service.index_document(
        db= state["db"],
        document_id=state["document_id"]
    )

    if not indexing_result:
        state["indexed"] = False
        state["success"] = False
        state["error"] = "Indexing failed. Document was not found."
        return state

    state["indexed"] = True
    state["indexing_result"] = indexing_result
    state["chunk_count"] = indexing_result.get("chunk_count", 0)
    state["stored_vector_count"] = indexing_result.get("stored_vector_count", 0)
    state["success"] = True
    state["error"] = None

    return state

def build_ingestion_graph():

    graph= StateGraph(IngestionGraphState)

    ## adding nodes
     
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

    graph.add_node(
        "save_document_to_db",
        save_document_to_db
    )

    graph.add_node(
        "index_document",
        index_document
    )

    #################### adding edges

    graph.add_edge(
        START,
        "validate_input"
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

    graph.add_conditional_edges(
        "save_document_to_db",
        route_after_db_save,
        {
            "continue": "index_document",
            "stop": END
        }
    )

    graph.add_edge(
        "index_document",
        END
    )

    return graph.compile()

source_routing_graph = build_ingestion_graph()
