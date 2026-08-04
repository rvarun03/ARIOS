# services/document_service.py

from ingestion.ingestion_router import ingest
from repositories.document_repository import DocumentRepository
from services.nlp_analysis_service import NLPAnalysisService
from utils.file_storage import FileStorageService
from repositories.document_chunk_repository import DocumentChunkRepository
from services.text_chunking_service import TextChunkingService
from services.embedding_service import EmbeddingService
from services.vector_store_services import VectorStoreService
from services.RAG_service import RAGService
from services.llm_service import LLM_Service

class DocumentService:

    def __init__(self):
        self.document_repository = DocumentRepository()
        self.nlp_service = NLPAnalysisService()
        self.file_storage_service = FileStorageService()
        self.chunk_repository = DocumentChunkRepository()
        self.chunking_service = TextChunkingService()
        self.embedding_service = EmbeddingService()
        self.vector_store_service = VectorStoreService()
        self.rag_service = RAGService()
        self.llm_service= LLM_Service()
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
            cleaned_text=analysis_result["text"]["cleaned_text"],
            cleaned_text_preview=analysis_result["text"]["preview"],
            nlp_metadata=analysis_result["analysis"]
        )

        index_result = self.index_document(
            db=db,
            document_id=saved_document.document_id
        )

        response = self._format_saved_document(
            saved_document=saved_document
        )

        response["indexing"] = index_result
        
        return response

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
            cleaned_text=analysis_result["text"]["cleaned_text"],
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
            "document_id": saved_document.document_id,
            "title": saved_document.title,
            "source_type": saved_document.source_type,
            "source_url": saved_document.source_url,
            "file_name": saved_document.file_name,
            "file_path": saved_document.file_path,
            "file_type": saved_document.file_type,
            "file_size": saved_document.file_size,
            "raw_text_length": len(saved_document.raw_text or ""),
            "cleaned_text_length": len(saved_document.cleaned_text or ""),
            "cleaned_text_preview": saved_document.cleaned_text_preview,
            "nlp_metadata": saved_document.nlp_metadata,
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
        
    def create_chunks_for_documents(
        self,
        db,
        document_id:int,
        chunk_size: int=500,
        overlap: int=50
    )-> dict | None:
        
        document = self.document_repository.get_document_by_id(
            db=db,
            document_id=document_id
        )

        if not document:
            return None
            
        chunks=self.chunking_service.chunk_text(
            text=document.raw_text,
            chunk_size=chunk_size,
            overlap=overlap
        )

        self.chunk_repository.delete_chunks_by_document_id(
            db=db,
            document_id=document_id
        )

        saved_chunks = self.chunk_repository.create_chunks(
            db=db,
            document_id=document_id,
            chunks=chunks
        )

        return {
            "message": "Document chunks created successfully",
            "document_id": document.document_id,
            "title": document.title,
            "chunk_count": len(saved_chunks),
            "chunk_size": chunk_size,
            "overlap": overlap
        }
        
    def get_chunks_for_document(
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

            chunks = self.chunk_repository.get_chunks_by_document_id(
                db=db,
                document_id=document_id
            )

            return {
                "document_id": document.document_id,
                "title": document.title,
                "chunk_count": len(chunks),
                "chunks": [
                    {
                        "chunk_id": chunk.chunk_id,
                        "chunk_index": chunk.chunk_index,
                        "chunk_text": chunk.chunk_text,
                        "word_count": chunk.word_count,
                        "char_count": chunk.char_count
                    }
                    for chunk in chunks
                ]
            }

    def generate_embeddings_for_document(
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
        
        chunks=self.chunk_repository.get_chunks_by_document_id(
            db=db,
            document_id=document_id
        )

        if not chunks:
            return {
                "document_id": document.document_id,
                "title": document.title,
                "message": "No chunks found. Create chunks first.",
                "embeddings": []
            }
        
        embeddings = self.embedding_service.embed_chunks(
            chunks=chunks
        )

        return {
            "document_id": document.document_id,
            "title": document.title,
            "chunk_count": len(chunks),
            "embedding_count": len(embeddings),
            "embeddings": embeddings
        }
    
    def store_document_embeddings(
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
        
        chunks=self.chunk_repository.get_chunks_by_document_id(
            db=db,
            document_id=document_id
        )

        if not chunks:
            return {
                "document_id": document.document_id,
                "title": document.title,
                "message": "No chunks found. Create chunks first.",
                "stored_count": 0
            }
        
        embeddings = self.embedding_service.embed_chunk_texts(
            chunks=chunks
        )

        result = self.vector_store_service.add_document_chunks(
            document=document,
            chunks=chunks,
            embeddings=embeddings
        )

        return {
            "message": "Document chunk embeddings stored in ChromaDB",
            "document_id": document.document_id,
            "title": document.title,
            "chunk_count": len(chunks),
            "stored_count": result["stored_count"]
        }
    
    def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        source_type: str | None = None,
        document_id: int | None = None
    ) -> dict:

        query_embedding = self.embedding_service.embed_text(
            query
        )

        results = self.vector_store_service.search_similar_chunks(
            query_embedding=query_embedding,
            top_k=top_k,
            source_type=source_type,
            document_id=document_id
        )

        return {
            "query": query,
            "top_k": top_k,
            "result_count": len(results),
            "results": results
        }

    def _get_documents_from_retrieved_chunks(
        self,
        db,
        retrieved_chunks: list[dict]
    ):

        document_ids = set()

        for result in retrieved_chunks:
            metadata = result.get("metadata", {})

            document_id = metadata.get("document_id")

            if document_id is not None:
                document_ids.add(
                    int(document_id)
                )

        documents = []

        for document_id in document_ids:
            document = self.document_repository.get_document_by_id(
                db=db,
                document_id=document_id
            )

            if document:
                documents.append(document)

        return documents

    def ask_question(
        self,
        db,
        question:str,
        top_k: int = 5,
        source_type: str | None = None,
        document_id: int | None = None
    ):
        search_result = self.semantic_search(
            query=question,
            top_k=top_k,
            source_type=source_type,
            document_id=document_id
        )

        retrieved_chunks = search_result.get("results", [])

        if not retrieved_chunks:
            return {
                "question": question,
                "answer": "I could not find this information in the provided documents.",
                "source_count": 0,
                "sources": []
            }

        context = self.rag_service.build_context(
            retrieved_chunks=retrieved_chunks
        )

        documents = self._get_documents_from_retrieved_chunks(
            db=db,
            retrieved_chunks=retrieved_chunks
        )

        metadata_context = self.rag_service.build_metadata_context(
            documents=documents
        )

        
        prompt = self.rag_service.build_prompt(
            question=question,
            context=context,
            metadata_context=metadata_context
        )

        answer = self.llm_service.generate_answer(
            prompt=prompt
        )

        return answer

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

    def get_vector_store_count(self) -> dict:
        return {
            "collection": "document_chunks",
            "stored_chunk_count": self.vector_store_service.count_chunks()
        }

    ####################### Main function #######################

    def index_document(
        self,
        db,
        document_id:int,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> dict | None:

        document = self.document_repository.get_document_by_id(
            db=db,
            document_id=document_id
        )

        if not document:
            return None

        text_for_indexing = document.cleaned_text or document.raw_text

        chunks = self.chunking_service.chunk_text(
            text=text_for_indexing,
            chunk_size=chunk_size,
            overlap=overlap
        )

        self.chunk_repository.delete_chunks_by_document_id(
            db=db,
            document_id=document_id
        )

        saved_chunks = self.chunk_repository.create_chunks(
            db=db,
            document_id=document.document_id,
            chunks=chunks
        )

        embeddings = self.embedding_service.embed_chunk_texts(
            chunks=saved_chunks
        )

        vector_result = self.vector_store_service.add_document_chunks(
            document=document,
            chunks=saved_chunks,
            embeddings=embeddings
        )

        return {
            "document_id": document.document_id,
            "chunk_count": len(saved_chunks),
            "stored_vector_count": vector_result["stored_count"],
            "indexed_text": "cleaned_text" if document.cleaned_text else "raw_text"
        }
