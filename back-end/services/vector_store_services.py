from pathlib import Path

import chromadb

class VectorStoreService:
    """
    Stores document chunk embeddings in ChromaDB.
    """

    def __init__(self):

        self.client=chromadb.PersistentClient(
            path=str(Path("chroma_db"))
        )

        self.collection = self.client.get_or_create_collection(
            name="document_chunks"
        )


    def add_document_chunks(
        self,
        document,
        chunks:list,
        embeddings: list[list[float]]
    ) -> dict:

        ids=[]
        documents=[]
        metadatas=[]

        for chunk, embedding in zip(chunks, embeddings):

            ids.append(
                f"document_{document.document_id}_chunk_{chunk.chunk_id}"
            )

            documents.append(chunk.text)

            metadatas.append(
                {
                    "document_id": document.document_id,
                    "chunk_id": chunk.chunk_id,
                    "chunk_index": chunk.chunk_index,
                    "title": document.title,
                    "source_type": document.source_type,
                    "source_url": document.source_url or "",
                    "file_path": document.file_path or ""
                }
            )      

        if not ids:
            return {
                "stored_count": 0
            }   

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        return {
            "stored_count": len(ids)
        } 
    
    def search_similar_chunks(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        source_type: str | None = None,
        document_id: int | None = None
    ) -> list[dict]:
        
        where_filters=[]

        if source_type:

            where_filters.append(
                {
                    "source_type": source_type
                }
            )

        if document_id:
            
            where_filters.append(
                {
                    "document_id": document_id
                }
            )

        where = None

        if len(where_filters)==1:
            where=where_filters[0]

        elif len(where_filters) > 1:
            where={
                "$and":where_filters
            }

        query_result = self.collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=top_k,
            where=where
        )   

        results = []

        ids = query_result.get("ids", [[]])[0]
        documents = query_result.get("documents", [[]])[0]
        metadatas = query_result.get("metadatas", [[]])[0]
        distances = query_result.get("distances", [[]])[0]

        for index in range(len(ids)):

            results.append(
                {
                    "id": ids[index],
                    "chunk_text": documents[index],
                    "metadata": metadatas[index],
                    "distance": distances[index]
                }
            )

        return results 
