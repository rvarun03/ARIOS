from sentence_transformers import SentenceTransformer

class EmbeddingService:

    def __init__(self):

        self.model=SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def embed_text(
        self,
        text:str
    ) -> list[float]:
        
        embedding= self.model.encode(
            text
        )

        return embedding.tolist()
    
    def embed_chunk_texts(
        self,
        chunks:list
    ) -> list[list[float]]:
        
        chunk_texts=[
            chunk.chunk_text
            for chunk in chunks
        ]

        embeddings=self.model.encode(
            chunk_texts
        )

        return [
            embedding.tolist()
            for embedding in embeddings
        ]
        
    def embed_chunks(
        self,
        chunks:list
    )-> list[dict]:
        
        results=[]

        for chunk in chunks:

            embedding = self.embed_text(
                chunk.chunk_text
            )

            results.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "chunk_index": chunk.chunk_index,
                    "embedding_dimension": len(embedding),
                    "embedding_preview": embedding[:5]
                }
            )

        return results    