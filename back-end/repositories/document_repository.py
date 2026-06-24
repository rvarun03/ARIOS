from sqlalchemy.orm import Session

from models.document import Document
from schemas.ingestion import IngestionOutput

import hashlib

class DocumentRepository:

    def generate_hash(
        self,
        text:str
    ) -> str:
        
        return hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

    def get_by_hash(
        self,
        db: Session,
        content_hash: str
    ):
        return(
            db.query(Document)
            .filter(
                Document.content_hash == content_hash
            )
            .first()
        )

    def get_all_documents(
        self,
        db:Session
    ):
        
        return(
            db.query(Document).
            all()
        )

    def create_document(
        self,    
        db: Session,
        document: IngestionOutput
    ):

        content_hash = self.generate_hash(
            document.raw_text
        )
        
        db_document = Document(
            title=document.title,
            source_type=document.source_type,
            source_url=document.source_url,
            raw_text=document.raw_text,
            content_hash=content_hash,
            metadata_json=document.metadata
        )

        db.add(db_document)

        db.commit()

        db.refresh(db_document)

        return db_document

