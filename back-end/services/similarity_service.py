from repositories.document_repository import (
    DocumentRepository
)

from services.corpus_service import get_corpus

from nlp.rankings.corpus_tfidf_extractor import (
    CorpusTFIDFExtractor
)

from nlp.similarity.cosine_similarity import (
    DocumentSimilarity
)

document_repo= DocumentRepository()

def get_similar_documents_service(
    db,
    document_index: int
):
    
    corpus= get_corpus(db)

    extractor= CorpusTFIDFExtractor(
        corpus=corpus
    )

    similarity= DocumentSimilarity(
        extractor.tfidf_matrix
    )

    similar_docs = (
        similarity.get_similar_documents(
            document_index
        )
    )

    documents = (
        document_repo.get_all_documents(db)
    )

    result = []

    for item in similar_docs:

        idx = item["document_index"]

        result.append(
            {
                "title": documents[idx].title,
                "score": item["score"]
            }
        )

    return result


