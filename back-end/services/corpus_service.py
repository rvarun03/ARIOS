from sqlalchemy.orm import Session

from repositories.document_repository import (
    DocumentRepository
)

document_repo = DocumentRepository()

def get_corpus(
    db: Session
):

    documents = document_repo.get_all_documents(
        db
    )

    return [
        document.raw_text
        for document in documents
    ]


def get_corpus_statistics(
    db: Session
):

    documents = document_repo.get_all_documents(
        db
    )

    return {
        "document_count": len(documents),

        "total_words": sum(
            len(doc.raw_text.split())
            for doc in documents
        ),

        "average_words_per_document": (
            sum(
                len(doc.raw_text.split())
                for doc in documents
            )
            / len(documents)
            if documents else 0
        )
    }