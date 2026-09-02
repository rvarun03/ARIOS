import spacy
from models.document_chunk import DocumentChunk
from models.document import Document
from sqlalchemy import or_

class DocumentChunkRepository:

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def delete_chunks_by_document_id(
        self,
        db,
        document_id: int
    ) -> None:

        db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).delete()

        db.commit()

    def create_chunks(
        self,
        db,
        document_id: int,
        chunks: list[dict]
    )-> list[dict]:

        chunk_records=[]

        for chunk in chunks:

            chunk_record = DocumentChunk(
                document_id=document_id,
                chunk_index=chunk["chunk_index"],
                chunk_text=chunk["chunk_text"],
                word_count=chunk["word_count"],
                char_count=chunk["char_count"]
            )

            chunk_records.append(
                chunk_record
            )
        
        db.add_all(
            chunk_records
        )

        db.commit()

        for chunk_record in chunk_records:
            db.refresh(
                chunk_record
            )    

        return chunk_records

    def get_chunks_by_document_id(
        self,
        db,
        document_id: int
    ) -> list[DocumentChunk]:

        return (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
            .all()
        )    


    def search_chunks_by_keywords(
        self,
        db,
        query: str,
        top_k: int = 10,
        source_type: str | None = None,
        document_id: int | None = None
    ) -> list[dict]:

        keywords=self.__extract_keywords(
            query=query
        )

        if not keywords:
            return []

        db_query=(
            db.query(DocumentChunk,Document)
            .join(
                Document,
                Document.document_id == DocumentChunk.document_id
            )
        )

        if document_id is not None:
            db_query=db_query.filter(
                Document.document_id == DocumentChunk.document_id
            )

        if source_type:
            db_query=db_query.filter(
                Document.source_type == source_type
            )

        keyword_filters=[]

        for keyword in keywords:
            keyword_filters.append(
                DocumentChunk.chunk_text.ilike(f"%{keyword}%")
            )

        db_query = db_query.filter(
            or_(*keyword_filters)
        )

        rows = db_query.all()

        scored_results = []

        for chunk,document in rows:
            
            keyword_score = self.__calculate_keyword_score(
                text=chunk.chunk_text,
                keywords=keywords
            )

            if keyword_score <= 0:
                continue

            scored_results.append(
                {
                    "id": f"keyword_document_{document.document_id}_chunk_{chunk.chunk_id}",
                    "chunk_text": chunk.chunk_text,
                    "metadata": {
                        "document_id": document.document_id,
                        "chunk_id": chunk.chunk_id,
                        "chunk_index": chunk.chunk_index,
                        "title": document.title,
                        "source_type": document.source_type,
                        "source_url": document.source_url or "",
                        "file_path": document.file_path or ""
                    },
                    "distance": None,
                    "keyword_score": keyword_score,
                    "retrieval_type": "keyword"
                }
            )

        scored_results = sorted(
            scored_results,
            key=lambda item: item["keyword_score"],
            reverse=True
        )

        return scored_results[:top_k]    
    
    ######## Helper functions

    def __extract_keywords(
        self,
        query:str
    )-> list[str]:

        if not query or not query.strip():
            return []

        doc = self.nlp(query)

        important_pos = {
            "PROPN",
            "NOUN",
            "VERB",
            "ADJ",
            "NUM"
        }

        keywords=[]

        for token in doc:

            if token.is_stop:
                continue

            if token.is_punct or token.is_space:
                continue

            if len(token.text.strip()) <= 1:
                continue

            if token.pos_ not in important_pos:
                continue

            token_text=token.lower()
            token_text = token.text.lower()
            token_lemma = token.lemma_.lower()

            keywords.append(token_text)

            if token_lemma != token_text:
                keywords.append(token_lemma)

        return self._remove_duplicates(keywords)

    def _remove_duplicates(
        self,
        items: list[str]
    ) -> list[str]:

        unique_items = []
        seen_items = set()

        for item in items:
            if item not in seen_items:
                unique_items.append(item)
                seen_items.add(item)

        return unique_items        

    def __calculate_keyword_score(
        self,
        text: str,
        keywords: list[str]
    ) -> int:

        text_lower = text.lower()
        score=0

        for keyword in keywords:
            score+= text_lower.count(keyword.lower())

        return score    