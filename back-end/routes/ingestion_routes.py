from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session

from schemas.ingestion import IngestionRequest
from services.ingestion_service import ingest_document_service
from core.database import get_db


router = APIRouter(
    prefix="/ingest", 
    tags=["Ingestion"]
    )

@router.post("/")
def ingest_document(
    request: IngestionRequest,
    db:Session = Depends(get_db)
    ):
    
    try:

        document = ingest_document_service(
            source_type=request.source_type,
            source=request.source,
            db=db
        )

        return {
            "id": document.id,
            "title": document.title,
            "source_type": document.source_type
        }
    
    except ValueError as e:

        raise HTTPException(
            status_code=409,
            detail=str(e)
        )


    