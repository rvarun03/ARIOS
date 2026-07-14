from models.document_chunk import DocumentChunk

class DocumentChunkRepository:

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