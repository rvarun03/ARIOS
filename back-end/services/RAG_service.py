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
            transformer_analysis = metadata.get("transformer_analysis", {})

            top_keywords = keywords[:10]
            top_entities = entities[:10]
            top_summary = summary[:3]

            document_type = transformer_analysis.get("document_type",{})
            best_predicted_label = transformer_analysis.get(
                "best_predicted_label",
                "not available"
            )
            confidence = transformer_analysis.get(
                "confidence",
                0.0
            )

            all_scores = transformer_analysis.get(
                "all_scores",
                []
            )

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

    Transformer Document Type:
    {document_type}

    Best Predicted Label:
    {best_predicted_label}

    Transformer Confidence:
    {confidence}
    
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
5. If the user asks about the document type, category, nature, or what kind of document it is:
   - Mention the document type predicted by the transformer classifier.
   - Mention the confidence score for that prediction.
   - If document_type is "uncertain", also mention the best_predicted_label as the closest label.
6. Keep the answer clear and structured.
7. Do not mention ChromaDB, embeddings, or internal implementation details.
8. Return the answer as a single paragraph.
9. Do not use bullet points, markdown, headings, or newline characters.
10. Do not put quotation marks around document types, labels, scores, or metadata values. Write blog article, not "blog article".

{metadata_section}

Retrieved Context:
{context}

User Question:
{question}

Answer:
"""    