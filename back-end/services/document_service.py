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
            {
                "document_id": document.document_id,
                "title": document.title,
                "source_type": document.source_type,
                "source_url": document.source_url,
                "file_name": document.file_name,
                "file_path": document.file_path,
                "created_at": document.created_at
            }
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