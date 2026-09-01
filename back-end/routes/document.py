# routes/document_routes.py

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.document import DocumentIngestRequest,AutoDocumentIngestRequest
from services.document_service import DocumentService

from schemas.rag_schema import AskDocumentRequest

from agents.ingestion_graph import source_routing_graph

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


document_service = DocumentService()


@router.post("/ingest")
def ingest_document(
    request: DocumentIngestRequest,
    db: Session = Depends(get_db)
):

    result = document_service.ingest_analyze_and_save(
        db=db,
        source_type=request.source_type,
        source=request.source
    )

    return result


@router.post("/upload")
def upload_document(
    source_type: Annotated[str, Form()],
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    result = document_service.upload_analyze_and_save(
        db=db,
        source_type=source_type,
        file=file
    )

    return result


@router.get("")
def get_documents(
    db: Session = Depends(get_db)
):

    return document_service.get_all_documents(
        db=db
    )

@router.get("/search")
def search_documents(
    title: str | None = None,
    source_type: str | None = None,
    keyword: str | None = None,
    entity: str | None = None,
    db: Session = Depends(get_db)
):

    return document_service.search_documents(
        db=db,
        title=title,
        source_type=source_type,
        keyword=keyword,
        entity=entity
    )

@router.get("/semantic-search")
def semantic_search_documents(
    query: str,
    top_k: int = 5,
    source_type: str | None = None,
    document_id: int | None = None
):

    return document_service.semantic_search(
        query=query,
        top_k=top_k,
        source_type=source_type,
        document_id=document_id
    )

@router.post("/{document_id}/chunks")
def create_document_chunks(
    document_id: int,
    chunk_size: int = 500,
    overlap: int = 50,
    db: Session = Depends(get_db)
):

    result = document_service.create_chunks_for_documents(
        db=db,
        document_id=document_id,
        chunk_size=chunk_size,
        overlap=overlap
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return result


@router.get("/{document_id}/chunks")
def get_document_chunks(
    document_id: int,
    db: Session = Depends(get_db)
):

    result = document_service.get_chunks_for_document(
        db=db,
        document_id=document_id
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return result

@router.post("/{document_id}/embeddings")
def generate_document_embeddings(
    document_id: int,
    db: Session = Depends(get_db)
):

    result = document_service.generate_embeddings_for_document(
        db=db,
        document_id=document_id
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return result

@router.post("/{document_id}/vector-store")
def store_document_embeddings(
    document_id: int,
    db: Session = Depends(get_db)
):

    result = document_service.store_document_embeddings(
        db=db,
        document_id=document_id
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return result

@router.get("/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = document_service.get_document_by_id(
        db=db,
        document_id=document_id
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document

@router.get("/vector-store/count")
def get_vector_store_count():

    return document_service.get_vector_store_count()

@router.post("/ask")
def ask_documents(
    request: AskDocumentRequest,
    db: Session = Depends(get_db)
):

    return document_service.ask_question(
        question=request.question,
        top_k=request.top_k,
        db=db,
        source_type=request.source_type,
        document_id=request.document_id
    )


@router.post("/graph/ingest")
def graph_ingest_document(
    request: AutoDocumentIngestRequest,
    db: Session = Depends(get_db)
):
    initial_state = {
        "db": db,
        "source_type": "",
        "source": request.source,
        "is_valid": False,
        "success": False,
        "title": "",
        "raw_text": "",
        "source_url": None,
        "file_name": None,
        "file_path": None,
        "file_type": None,
        "file_size": None,
        "metadata": {},
        "analysis_result": {},
        "cleaned_text_length": 0,
        "document_type": "",
        "document_type_confidence": 0.0,
        "document_id": None,
        "saved_to_db": False,
        "indexed": False,
        "indexing_result": {},
        "chunk_count": 0,
        "stored_vector_count": 0,
        "error": None
    }

    result = source_routing_graph.invoke(
        initial_state
    )

    return {
        "success": result["success"],
        "is_valid": result["is_valid"],
        "document_id": result["document_id"],
        "title": result["title"],
        "source_type": result["source_type"],
        "source_url": result["source_url"],
        "cleaned_text_length": result["cleaned_text_length"],
        "document_type": result["document_type"],
        "document_type_confidence": result["document_type_confidence"],
        "saved_to_db": result["saved_to_db"],
        "indexed": result["indexed"],
        "chunk_count": result["chunk_count"],
        "stored_vector_count": result["stored_vector_count"],
        "indexing_result": result["indexing_result"],
        "error": result["error"]
    }

@router.post("/graph/upload")
def graph_upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    saved_file = document_service.file_storage_service.save_uploaded_file(
        file=file,
        source_type="pdf"
    )

    initial_state = {
        "db": db,
        "source_type": "",
        "source": saved_file["file_path"],
        "is_valid": False,
        "success": False,
        "title": "",
        "raw_text": "",
        "source_url": None,
        "file_name": saved_file["file_name"],
        "file_path": saved_file["file_path"],
        "file_type": saved_file["file_type"],
        "file_size": saved_file["file_size"],
        "metadata": {},
        "analysis_result": {},
        "cleaned_text_length": 0,
        "document_type": "",
        "document_type_confidence": 0.0,
        "document_id": None,
        "saved_to_db": False,
        "indexed": False,
        "indexing_result": {},
        "chunk_count": 0,
        "stored_vector_count": 0,
        "error": None
    }

    result = source_routing_graph.invoke(initial_state)

    return {
        "success": result["success"],
        "is_valid": result["is_valid"],
        "document_id": result["document_id"],
        "title": result["title"],
        "source_type": result["source_type"],
        "source": result["file_path"],
        "file_name": result["file_name"],
        "file_type": result["file_type"],
        "file_size": result["file_size"],
        "cleaned_text_length": result["cleaned_text_length"],
        "document_type": result["document_type"],
        "document_type_confidence": result["document_type_confidence"],
        "saved_to_db": result["saved_to_db"],
        "indexed": result["indexed"],
        "chunk_count": result["chunk_count"],
        "stored_vector_count": result["stored_vector_count"],
        "indexing_result": result["indexing_result"],
        "error": result["error"]
    }
