class TextChunkingService:
    """
    Splits long document text into smaller chunks.

    For now we use word-based chunking.
    Later we can upgrade this to token-based chunking.
    """

    def chunk_text(
        self,
        text:str,
        chunk_size:int=500,
        overlap:int=50
    )-> list[dict]:
        
        if not text or not text.strip():
            return []
        
        if chunk_size <=0:
            raise ValueError(
                "Chunk size must be greater than 0"
            )
        
        if overlap < 0:
            raise ValueError(
                "overlap cannot be negative"
            )

        if overlap >= chunk_size:
            raise ValueError(
                "overlap must be smaller than chunk_size"
            )
        
        words=text.split()

        chunks=[]

        start=0

        while start < len(words):

            end=min(
                start+chunk_size,
                len(words)
            )

            chunk_words= words[start:end]

            chunk_text= " ".join(chunk_words)

            chunks.append(
                {
                    "chunk_index": len(chunks),
                    "chunk_text": chunk_text,
                    "word_count": len(chunk_words),
                    "char_count": len(chunk_text)
                }
            )

            if end == len(words):
                break

            start= end - overlap

        return chunks        