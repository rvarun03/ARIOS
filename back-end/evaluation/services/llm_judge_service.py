import json
import re

from services.llm_service import LLM_Service


class LLMJudgeService:

    def __init__(self):
        self.llm_service = LLM_Service()

    def evaluate_answer(
        self,
        question: str,
        expected_answer: str,
        generated_answer: str,
        sources: list[dict]
    ) -> dict:

        context = self._build_context_from_sources(
            sources=sources
        )

        prompt = self._build_judge_prompt(
            question=question,
            expected_answer=expected_answer,
            generated_answer=generated_answer,
            context=context
        )

        response = self.llm_service.generate_answer(
            prompt=prompt
        )

        return self._parse_judge_response(
            response=response
        )

    def _build_context_from_sources(
        self,
        sources: list[dict],
        max_sources: int = 5,
        max_chars_per_source: int = 1500
    ) -> str:

        context_parts = []

        for source in sources[:max_sources]:
            chunk_id = source.get("chunk_id")
            document_id = source.get("document_id")
            title = source.get("title")
            chunk_text = source.get("chunk_text", "")

            chunk_text = chunk_text[:max_chars_per_source]

            context_parts.append(
                f"""
SOURCE:
document_id: {document_id}
chunk_id: {chunk_id}
title: {title}
text:
{chunk_text}
"""
            )

        return "\n".join(context_parts)

    def _build_judge_prompt(
        self,
        question: str,
        expected_answer: str,
        generated_answer: str,
        context: str
    ) -> str:

        return f"""
You are an evaluator for a RAG system.

Your task is to evaluate the generated answer using:
1. The user question
2. The expected answer
3. The retrieved source context
4. The generated answer

Evaluate these:

correctness_score:
- 1.0 means the generated answer is fully correct compared to expected answer
- 0.5 means partially correct
- 0.0 means incorrect

faithfulness_score:
- 1.0 means the answer is fully supported by the retrieved context
- 0.5 means partially supported
- 0.0 means not supported by the context

relevance_score:
- 1.0 means the answer directly answers the question
- 0.5 means partially answers
- 0.0 means does not answer the question

hallucination:
- true if the answer contains unsupported or invented information
- false if the answer is supported by the context

Return JSON only.
Do not add markdown.
Do not add explanation outside JSON.

Question:
{question}

Expected Answer:
{expected_answer}

Retrieved Context:
{context}

Generated Answer:
{generated_answer}

Return JSON in this exact format:
{{
  "correctness_score": 0.0,
  "faithfulness_score": 0.0,
  "relevance_score": 0.0,
  "hallucination": true,
  "reason": "short reason"
}}
"""

    def _parse_judge_response(
        self,
        response: str
    ) -> dict:

        default_response = {
            "correctness_score": 0.0,
            "faithfulness_score": 0.0,
            "relevance_score": 0.0,
            "hallucination": True,
            "reason": "Failed to parse judge response."
        }

        if not response or not response.strip():
            return default_response

        response = response.strip()

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        json_match = re.search(r"\{[\s\S]*\}", response)

        if not json_match:
            return default_response

        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            return default_response