from sklearn.metrics.pairwise import (
    cosine_similarity
)

class DocumentSimilarity:

    def __init__(
        self,
        tfidf_matrix
    ):
        
        self.similarity_matrix= (
            cosine_similarity(
                tfidf_matrix
            )
        )

    def get_similarity_matrix(self):

        return (
            self.similarity_matrix
            .tolist()
        )
    
    def get_similar_documents(
        self,
        document_index: int,
        top_k: int = 5
    ):

        similarities = (
            self.similarity_matrix[
                document_index
            ]
        )

        ranked = sorted(
            enumerate(similarities),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {
                "document_index": idx,
                "score": round(float(score), 4)
            }
            for idx, score in ranked
            if idx != document_index
        ][:top_k]