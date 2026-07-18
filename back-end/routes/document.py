# routes/document_routes.py

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.document import DocumentIngestRequest
from services.document_service import DocumentService


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