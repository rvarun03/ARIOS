# repositories/document_repository.py

from models.document import Document


class DocumentRepository:

    def create_document(
        self,
        db,
        title: str,
        source_type: str,
        source_url: str | None,
        raw_text: str,
        cleaned_text_preview: str,
        nlp_metadata: dict,
        file_name: str | None = None,
        file_path: str | None = None,
        file_type: str | None = None,
        file_size: int | None = None
    ) -> Document:

        document = Document(
            title=title,
            source_type=source_type,
            source_url=source_url,
            file_name=file_name,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            raw_text=raw_text,
            cleaned_text_preview=cleaned_text_preview,
            nlp_metadata=nlp_metadata
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    def get_all_documents(
        self,
        db
    ) -> list[Document]:

        return (
            db.query(Document)
            .order_by(Document.created_at.desc())
            .all()
        )

    def get_document_by_id(
        self,
        db,
        document_id: int
    ) -> Document | None:

        return (
            db.query(Document)
            .filter(Document.document_id == document_id)
            .first()
        )
    
    def search_documents(
        self,
        db,
        title: str | None = None,
        source_type: str | None = None
    ) -> list[Document]:
        
        query= db.query(Document)

        if title:
            query=query.filter(
                Document.title.ilike(f"%{title}%")
            )

        if source_type:
            query=query.filter(
                Document.source_type == source_type
            )    

        return (
            query
            .order_by(Document.created_at.desc())
            .all()
        )    
