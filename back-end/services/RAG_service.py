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

    def build_metadata_context(
        self,
        documents:list
    ) -> str:

        metadata_parts=[]

        for document in documents:

            nlp_metadata=document.nlp_metadata or {}

            metadata= nlp_metadata.get("metadata", {})

            keywords= metadata.get("keywords", {})
            entities= metadata.get("entities", {})
            summary = metadata.get("summary", [])

            top_keywords = keywords[:10]
            top_entities = entities[:10]
            top_summary = summary[:3]

            keyword_text = [
                item.get("keyword", "")
                for item in top_keywords
                if isinstance(item, dict)
            ]

            entity_text = [
                item.get("text", "")
                for item in top_entities
                if isinstance(item, dict)
            ]

            summary_text = [
                item.get("sentence", "")
                for item in top_summary
                if isinstance(item, dict)
            ]

            metadata_parts.append(
                f"""
    Document Title: {document.title}
    Document ID: {document.document_id}

    Top Keywords:
    {", ".join(keyword_text)}

    Important Entities:
    {", ".join(entity_text)}

    Document Summary:
    {" ".join(summary_text)}
    """
            )

        return "\n\n".join(metadata_parts)    

    def build_prompt(
        self,
        question: str,
        context: str,
        metadata_context: str | None = None
    ) -> str:

        metadata_section =""

        if metadata_context:

            metadata_section=  f"""
                Document Metadata:
                {metadata_context}
            """

        return f"""
You are ARIOS, an AI research intelligence assistant.

Answer the user's question using only the provided document context and metadata.

Rules:
1. Do not make up information.
2. If the answer is not present in the context, say:
   "I could not find this information in the provided documents."
3. Prefer the retrieved chunk content as the main source.
4. Use document metadata only to understand the document better.
5. Keep the answer clear and structured.
6. Do not mention ChromaDB, embeddings, or internal implementation details.

{metadata_section}

Retrieved Context:
{context}

User Question:
{question}

Answer:
"""    