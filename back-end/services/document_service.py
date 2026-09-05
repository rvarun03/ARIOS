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
from services.s3_service import S3Service
from services.query_expansion_service import QueryExpansionService

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
        self.s3_service = S3Service()
        self.query_expansion_service = QueryExpansionService()
        
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

        s3_upload_result = self.s3_service.upload_file(
            file=file,
            folder="uploads"
        )

        if not s3_upload_result.get("uploaded"):
            return {
                "uploaded": False,
                "error": "File was saved locally but failed to upload to S3.",
                "s3_error": s3_upload_result.get("error"),
                "local_file": saved_file
            }
        
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
            file_size=saved_file["file_size"],
            s3_key=s3_upload_result["s3_key"],
            s3_uri=s3_upload_result["s3_uri"],
            s3_bucket=s3_upload_result["bucket"]
        )

        index_result = self.index_document(
            db=db,
            document_id=saved_document.document_id
        )

        response = self._format_saved_document(
            saved_document=saved_document
        )

        response["s3"] = {
            "uploaded": True,
            "bucket": s3_upload_result["bucket"],
            "s3_key": s3_upload_result["s3_key"],
            "s3_uri": s3_upload_result["s3_uri"]
        }

        response["indexing"] = index_result

        return response

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
            "s3_key": saved_document.s3_key,
            "s3_uri": saved_document.s3_uri,
            "s3_bucket": saved_document.s3_bucket,
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

    ## hybrid_search

    def hybrid_search(
        self,
        db,
        question:str,
        top_k: int =5,
        source_type: str | None = None,
        document_id: int | None = None
    )->dict:
        
        expanded_queries = self.query_expansion_service.generate_search_queries(
            question=question,
            max_queries=4
        )

        if not expanded_queries:
            expanded_queries = [question]

        all_results=[]

        search_top_k = max(top_k, 10)

        for expanded_query in expanded_queries:  

            semantic_search_result = self.semantic_search(
                query= expanded_query,
                top_k= search_top_k,
                source_type=source_type,
                document_id=document_id
            ) 

            semantic_results = semantic_search_result.get("results", [])

            for rank,result in enumerate(semantic_results, start=1):

                result=dict(result)

                result["retrieval_type"] = "semantic"
                result["search_query"] = expanded_query
                result["semantic_rank"] = rank
                result["hybrid_score"] = self._calculate_rank_fusion_score(
                    rank=rank,
                    weight=1.0
                )
                all_results.append(result)

            keyword_results = self.chunk_repository.search_chunks_by_keywords(
                db=db,
                query=expanded_query,
                top_k=search_top_k,
                source_type=source_type,
                document_id=document_id
            )

            for rank, result in enumerate(keyword_results, start=1):
                result = dict(result)

                result["retrieval_type"] = "keyword"
                result["search_query"] = expanded_query
                result["keyword_rank"] = rank
                result["hybrid_score"] = self._calculate_rank_fusion_score(
                    rank=rank,
                    weight=0.3
                )

                all_results.append(result)    

        merged_results = self._merge_hybrid_results(
            results=all_results,
            top_k=top_k
        )    

        final_results = merged_results[:top_k]

        expanded_results = self._expand_with_neighbor_chunks(
            db=db,
            results=final_results,
            window_size=1
        )

        return {
            "query": question,
            "expanded_queries": expanded_queries,
            "top_k": top_k,
            "result_count": len(expanded_results),
            "retrieval_mode": "hybrid_rank_fusion_with_neighbors",
            "results": expanded_results
        }

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

        # search_result = self.hybrid_search(
        #     db=db,
        #     question=question,
        #     top_k=top_k,
        #     source_type=source_type,
        #     document_id=document_id
        # )

        retrieved_chunks = search_result.get("results", [])
        retrieval_debug = []

        for index, chunk in enumerate(retrieved_chunks, start=1):
            metadata = chunk.get("metadata", {})

            retrieval_debug.append(
                {
                    "rank": index,
                    "document_id": metadata.get("document_id"),
                    "chunk_id": metadata.get("chunk_id"),
                    "chunk_index": metadata.get("chunk_index"),
                    "title": metadata.get("title"),
                    "retrieval_type": chunk.get("retrieval_type"),
                    "retrieval_types": chunk.get("retrieval_types"),
                    "hybrid_score": chunk.get("hybrid_score"),
                    "semantic_fusion_score": chunk.get("semantic_fusion_score"),
                    "keyword_fusion_score": chunk.get("keyword_fusion_score"),
                    "distance": chunk.get("distance"),
                    "keyword_score": chunk.get("keyword_score"),
                    "matched_search_queries": chunk.get("matched_search_queries"),
                    "chunk_text_preview": chunk.get("chunk_text", "")[:2000]
                }
            )
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

        # LLMs may still wrap labels in quotes even when the prompt asks them
        # not to. Remove those presentation characters before JSON encoding.
        clean_answer = answer.strip().replace('"', "")

        evaluation = self._build_rag_evaluation(
            retrieved_chunks=retrieved_chunks,
            documents=documents,
            top_k=top_k,
            metadata_used=bool(metadata_context)
        )

        return {
        "question": question,
        "answer": clean_answer,
        "metadata_used": bool(metadata_context),
        "retrieval_debug": retrieval_debug,
        "retrieval_mode": search_result.get("retrieval_mode"),
        "expanded_queries": search_result.get("expanded_queries"),
        "evaluation": evaluation
    }


    def _build_rag_evaluation(
        self,
        retrieved_chunks: list[dict],
        documents: list,
        top_k: int,
        metadata_used: bool
    ):

        distances=[]

        for chunk in retrieved_chunks:

            distance = chunk.get("distance")

            if distance is not None:
                distances.append(float(distance))

        average_distance = None
        best_distance = None
        worst_distance = None

        if distances:

            average_distance = round(
                sum(distances)/len(distances),
                4
            )
            best_distance = round(
                min(distances),
                4
            )

            worst_distance = round(
                max(distances),
                4
            )    

        document_type = None
        best_predicted_label = None
        document_type_confidence = None
        confidence_threshold = None    

        if documents:

            first_document=documents[0]

            nlp_metadata = first_document.nlp_metadata or {}

            transformer_analysis= (
                nlp_metadata.get("metadata",{})
                .get("transformer_analysis", {})
            )

            document_type = transformer_analysis.get("document_type")
            best_predicted_label = transformer_analysis.get("best_predicted_label")
            document_type_confidence = transformer_analysis.get("confidence")
            confidence_threshold = transformer_analysis.get("confidence_threshold")

        return {
            "retrieved_chunk_count": len(retrieved_chunks),
            "requested_top_k": top_k,
            "metadata_used": metadata_used,
            "answer_generated": True,
            "average_distance": average_distance,
            "best_distance": best_distance,
            "worst_distance": worst_distance,
            "document_type": document_type,
            "best_predicted_label": best_predicted_label,
            "document_type_confidence": document_type_confidence,
            "confidence_threshold": confidence_threshold
        }    


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

## Helpers

    def _merge_hybrid_results(
        self,
        results: list[dict],
        top_k: int
    )-> list[dict]:

        merged_results={}

        for result in results:

            metadata = result.get('metadata',{})

            document_id = metadata.get("document_id")
            chunk_id = metadata.get("chunk_id")

            if document_id is None or chunk_id is None:
                continue

            result_key= f"{document_id}_{chunk_id}"

            retrieval_type = result.get(
                "retrieval_type",
                "unknown"
            )    

            retrieval_type = result.get(
                "retrieval_type",
                "unknown"
            )

            search_query = result.get("search_query")

            result_score = float(
                result.get("hybrid_score") or 0
            )

            if result_key not in merged_results:
                new_result= dict(result)
                new_result["retrieval_types"] = []
                new_result["matched_search_queries"] = []

                new_result["_semantic_fusion_score"] = 0.0
                new_result["_keyword_fusion_score"] = 0.0
                new_result["hybrid_score"] = 0.0

                merged_results[result_key] = new_result

            existing_result = merged_results[result_key]

            if retrieval_type not in  existing_result["retrieval_types"]:
                existing_result["retrieval_types"].append(retrieval_type)

            existing_result["retrieval_type"] = "+".join(
                existing_result["retrieval_types"]
            )    

            if search_query and search_query not in existing_result["matched_search_queries"]:
                existing_result["matched_search_queries"].append(search_query)

            if retrieval_type == "semantic":
                existing_result["_semantic_fusion_score"] = max(
                    existing_result["_semantic_fusion_score"],
                    result_score
                )      

            if retrieval_type == "keyword":
                existing_result["_keyword_fusion_score"] = max(
                    existing_result["_keyword_fusion_score"],
                    result_score
                )       

            existing_result["hybrid_score"] = round(
                existing_result["_semantic_fusion_score"]
                + existing_result["_keyword_fusion_score"],
                4
            )    

            existing_result["hybrid_score"] = round(
                existing_result["_semantic_fusion_score"]
                + existing_result["_keyword_fusion_score"],
                4
            )  

            existing_keyword_score = existing_result.get("keyword_score") or 0
            new_keyword_score = result.get("keyword_score") or 0

            existing_result["keyword_score"] = max(
                existing_keyword_score,
                new_keyword_score
            )

            existing_distance = existing_result.get("distance")
            new_distance = result.get("distance")

            if new_distance is not None:
                if existing_distance is None:
                    existing_result["distance"] = new_distance
                else:
                    existing_result["distance"] = min(
                        float(existing_distance),
                        float(new_distance)
                    )

        final_results = list(
            merged_results.values()
        )            
        for result in final_results:
            result["semantic_fusion_score"] = result.pop(
                "_semantic_fusion_score",
                0.0
            )
            result["keyword_fusion_score"] = result.pop(
                "_keyword_fusion_score",
                0.0
            )

        final_results = sorted(
            final_results,
            key=lambda item: item["hybrid_score"],
            reverse=True
        )

        return final_results[:top_k]    
            
        # merged_results={}

        # for result in results:
        #     metadata = result.get("metadata", {})

        #     document_id = metadata.get("document_id")
        #     chunk_id = metadata.get("chunk_id")

        #     if document_id is None or chunk_id is None:
        #         continue

        #     result_key = f"{document_id}_{chunk_id}"

        #     result_score = float(
        #         result.get("hybrid_score") or 0
        #     ) 

        #     retrieval_type = result.get(
        #         "retrieval_type",
        #         "unknown"
        #     )

        #     search_query = result.get("search_query")

        #     if result_key not in merged_results:

        #         new_result = dict(result)

        #         new_result["hybrid_score"] = result_score
        #         new_result["retrieval_types"] = [retrieval_type]
        #         new_result["matched_search_queries"] = []

        #         if search_query:
        #             new_result["matched_search_queries"].append(search_query)

        #         merged_results[result_key] = new_result    

        #     else:

        #         existing_result = merged_results[result_key]

        #         existing_result["hybrid_score"] += result_score

        #         if retrieval_type not in existing_result["retrieval_type"]:
        #             existing_result["retrieval_types"].append(retrieval_type)

        #         existing_result["retrieval_type"] = "+".join(
        #             existing_result["retrieval_types"]
        #         )    

        #         if search_query and search_query not in existing_result["matched_search_queries"]:
        #             existing_result["matched_search_queries"].append(search_query)

        #         existing_keyword_score = existing_result.get("keyword_score") or 0
        #         new_keyword_score = result.get("keyword_score") or 0 

        #         existing_result["keyword_score"] = max(
        #             existing_keyword_score,
        #             new_keyword_score
        #         )    

        #         existing_distance = existing_result.get("distance")
        #         new_distance = result.get("distance")

        #         if new_distance is not None:
        #             if existing_distance is None:
        #                 existing_result["distance"] = new_distance
        #             else:
        #                 existing_result["distance"] = min(
        #                     float(existing_distance),
        #                     float(new_distance)
        #                 )    

        # final_results = list(
        #     merged_results.values()
        # )                

        # final_results = sorted(
        #     final_results,
        #     key = lambda item: item["hybrid_score"],
        #     reverse=True
        # )

        # return final_results[:top_k]
                
                   

    def _calculate_semantic_hybrid_search(
        self,
        distance,
        rank: int
    )-> float:

        if distance is None:
            return 0.0

        distance=float(distance)

        semantic_score = 1 / (1 + distance)
        rank_bonus = 1 / rank

        return round(
            (semantic_score * 100) + (rank_bonus * 10),
            4
        )

    def _calculate_semantic_hybrid_score(
        self,
        keyword_score,
        rank: int
    ) -> float:

        if keyword_score is None:
            return 0.0

        keyword_score = float(keyword_score)
        rank_bonus = 1 / rank

        return round(
            keyword_score + (rank_bonus * 20),
            4
        )

    def _calculate_rank_fusion_score(
        self,
        rank: int,
        weight: float = 1.0
    ) -> float:

        return round(
            weight * (1 / rank),
            4
        )

    def _expand_with_neighbor_chunks(
        self,
        db,
        results: list[dict],
        window_size: int = 1
    ) -> list[dict]:

        expanded_results = []

        for result in results:
            metadata = result.get("metadata", {})

            document_id = metadata.get("document_id")
            chunk_index = metadata.get("chunk_index")

            if document_id is None or chunk_index is None:
                expanded_results.append(result)
                continue

            neighbor_chunks = self.chunk_repository.get_neighbor_chunks(
                db=db,
                document_id=int(document_id),
                chunk_index=int(chunk_index),
                window_size=window_size
            )

            combined_text_parts = []
            neighbor_debug = []

            for chunk in neighbor_chunks:
                combined_text_parts.append(
                    f"[Chunk index {chunk.chunk_index}]\n{chunk.chunk_text}"
                )

                neighbor_debug.append(
                    {
                        "chunk_id": chunk.chunk_id,
                        "chunk_index": chunk.chunk_index
                    }
                )

            expanded_result = dict(result)

            expanded_result["original_chunk_text"] = result.get("chunk_text", "")
            expanded_result["chunk_text"] = "\n\n".join(combined_text_parts)
            expanded_result["neighbor_expanded"] = True
            expanded_result["neighbor_window_size"] = window_size
            expanded_result["neighbor_chunks"] = neighbor_debug

            expanded_results.append(expanded_result)

        return expanded_results
        