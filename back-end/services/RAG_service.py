class RAGService:
    """
    Builds RAG context, prompt, and source output.
    """

    def build_context(
        self,
        retrieved_chunks = list[dict]
    ) ->str :

        context_parts=[]

        for index, result in enumerate(retrieved_chunks):
            metadata = result.get("metadata", {})

            title = metadata.get("title", "Unknown")
            chunk_index = metadata.get("chunk_index", "Unknown")
            chunk_text = result.get("chunk_text", "")

            context_parts.append(

                f"""
                Source {index}
                Title: {title}
                Chunk Index: {chunk_index}

                Content:
                {chunk_text}
                """
                
            )

        return "\n\n".join(context_parts)