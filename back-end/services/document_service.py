# services/document_service.py

from ingestion.ingestion_router import ingest
from repositories.document_repository import DocumentRepository
from services.nlp_analysis_service import NLPAnalysisService
from utils.file_storage import FileStorageService


class DocumentService:

    def __init__(self):
        self.document_repository = DocumentRepository()
        self.nlp_service = NLPAnalysisService()
        self.file_storage_service = FileStorageService()

    def ingest_analyze_and_save(
        self,
        db,
        source_type: str,
        source: str
    ) -> dict:

        ingestion_result = ingest(
            source_type=source_type,
            source=source
        )

        analysis_result = self.nlp_service.analyse_document(
            ingestion_result=ingestion_result,
            max_summary_sentences=5
        )

        
        saved_document = self.document_repository.create_document(
            db=db,
            title=analysis_result["title"],
            source_type=analysis_result["source_type"],
            source_url=analysis_result["source_url"],
            raw_text=ingestion_result.raw_text,
            cleaned_text_preview=analysis_result["text"]["preview"],
            nlp_metadata=analysis_result["analysis"]
        )

        return self._format_saved_document(
            saved_document=saved_document
        )

    def upload_analyze_and_save(
        self,
        db,
        source_type: str,
        file
    ) -> dict:

        saved_file = self.file_storage_service.save_uploaded_file(
            file=file,
            source_type=source_type
        )

        ingestion_result = ingest(
            source_type=source_type,
            source=saved_file["file_path"]
        )

        analysis_result = self.nlp_service.analyse_document(
            ingestion_result=ingestion_result,
            max_summary_sentences=5
        )

        document_title = (
            analysis_result.get("title")
            or saved_file.get("file_name")
            or "Untitled Document"
        )

        saved_document = self.document_repository.create_document(
            db=db,
            title=document_title,
            source_type=analysis_result["source_type"],
            source_url=analysis_result["source_url"],
            raw_text=ingestion_result.raw_text,
            cleaned_text_preview=analysis_result["text"]["preview"],
            nlp_metadata=analysis_result["analysis"],
            file_name=saved_file["file_name"],
            file_path=saved_file["file_path"],
            file_type=saved_file["file_type"],
            file_size=saved_file["file_size"]
        )

        return self._format_saved_document(
            saved_document=saved_document
        )

    def get_all_documents(
        self,
        db
    ) -> list[dict]:

        documents = self.document_repository.get_all_documents(
            db
        )

        return [
            self._format_document_list_item(
                document=document
            )
            for document in documents
        ]
    
    def get_document_by_id(
        self,
        db,
        document_id: int
    ) -> dict | None:

        document = self.document_repository.get_document_by_id(
            db=db,
            document_id=document_id
        )

        if not document:
            return None

        return self._format_saved_document(
            saved_document=document
        )

    def _format_saved_document(
        self,
        saved_document
    ) -> dict:

        return {
            "message": "Document saved successfully",
            "document_id": saved_document.document_id,
            "title": saved_document.title,
            "source_type": saved_document.source_type,
            "source_url": saved_document.source_url,
            "file": {
                "file_name": saved_document.file_name,
                "file_path": saved_document.file_path,
                "file_type": saved_document.file_type,
                "file_size": saved_document.file_size
            },
            "cleaned_text_preview": saved_document.cleaned_text_preview,
            "analysis": saved_document.nlp_metadata,
            "created_at": saved_document.created_at
        }
    
    def search_documents(
        self,
        db,
        title: str | None = None,
        source_type: str | None = None,
        keyword: str | None = None,
        entity: str | None = None
    ) -> list[dict]:
        
        documents = self.document_repository.search_documents(
            db=db,
            title=title,
            source_type=source_type
        )

        filtered_documents=[]

        for document in documents:
             
            if keyword and not self._document_has_keyword(
                document=document,
                keyword=keyword
            ):
                continue

            if entity and not self._document_has_entity(
                document=document,
                entity=entity
            ):
                continue

            filtered_documents.append(
                self._format_document_list_item(
                    document=document
                )
            )

            return filtered_documents

    def _document_has_keyword(
        self,
        document,
        keyword: str
    ) -> bool:
        
        metadata= document.nlp_metadata or {}

        keywords=(
            metadata
            .get("metadata", {})
            .get("keywords", {})
        )

        keyword = keyword.lower()

        for item in keywords:

            if isinstance(item,dict):
                
                stored_keyword=item.get(
                    "keyword",""
                )

            else:
                
                stored_keyword = str(item).lower(
                )

            if keyword.lower() in stored_keyword:
                return True

        return False      

    def _document_has_entity(
        self,
        document,
        entity: str
    ) -> bool:

        metadata = document.nlp_metadata or {}

        entities = (
            metadata
            .get("metadata", {})
            .get("entities", [])
        )

        entity_lower = entity.lower()

        for item in entities:

            if isinstance(item, dict):
                stored_entity = (
                    item.get("text", "")
                    .lower()
                )

            else:
                stored_entity = str(item).lower()

            if entity_lower in stored_entity:
                return True

        return False  
    
    def _format_document_list_item(
        self,
        document
    ) -> dict:

        metadata = document.nlp_metadata or {}

        statistics = metadata.get(
            "statistics",
            {}
        )

        return {
            "document_id": document.document_id,
            "title": document.title,
            "source_type": document.source_type,
            "source_url": document.source_url,
            "file_name": document.file_name,
            "file_path": document.file_path,
            "statistics": statistics,
            "created_at": document.created_at
        }