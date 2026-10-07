from sentence_transformers import CrossEncoder

class RerankerService:

    def __init__(self):
        self.model= CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    def rerank(
        self,
        chunks:list[dict],
        question:str,
        top_k: int=5
    )-> list[dict]:

        if not question or not question.strip():
            return chunks[:top_k]

        if not chunks:
            return []

        pairs=[]

        for chunk in chunks:
            chunk_text=chunk.get("chunk_text","")
            pairs.append(
                [
                    question,
                    chunk_text
                ]
            )

        scores=self.model.predict(pairs)

        reranked_chunks=[]

        for chunk,score in zip(chunks,scores):
            reranked_chunk=dict(chunk)
            reranked_chunk["reranker_score"] = round(float(score), 4)

            reranked_chunks.append(reranked_chunk)

        reranked_chunks = sorted(
            reranked_chunks,
            key=lambda item: item["reranker_score"],
            reverse=True
        )

        return reranked_chunks[:top_k]
