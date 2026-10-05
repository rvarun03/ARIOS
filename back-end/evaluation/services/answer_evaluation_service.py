import json
from pathlib import Path

from services.document_service import DocumentService
from evaluation.services.llm_judge_service import LLMJudgeService


class AnswerEvaluationService:

    def __init__(self):
        self.document_service = DocumentService()
        self.llm_judge_service = LLMJudgeService()

    def load_dataset(self, dataset_path: str) -> list[dict]:
        path = Path(dataset_path)

        if not path.exists():
            raise FileNotFoundError(f"Evaluation dataset not found: {dataset_path}")

        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def evaluate_dataset(
        self,
        db,
        dataset_path: str,
        top_k: int = 5
    ) -> dict:

        dataset = self.load_dataset(dataset_path=dataset_path)

        results = []

        for item in dataset:
            question = item["question"]
            expected_answer = item.get("expected_answer", "")
            reference_chunk_ids = item.get("relevant_chunk_ids", [])
            source_type = item.get("source_type")
            document_id = item.get("document_id")

            ask_result = self.document_service.ask_question(
                db=db,
                question=question,
                top_k=top_k,
                source_type=source_type,
                document_id=document_id
            )

            generated_answer = ask_result.get("answer", "")
            sources = ask_result.get("sources", [])

            predicted_chunk_ids = self._extract_source_chunk_ids(
                sources=sources
            )

            citation_evaluation = self._evaluate_citation_support(
                predicted_chunk_ids=predicted_chunk_ids,
                reference_chunk_ids=reference_chunk_ids
            )

            judge_evaluation = self.llm_judge_service.evaluate_answer(
                question=question,
                expected_answer=expected_answer,
                generated_answer=generated_answer,
                sources=sources
            )

            results.append(
                {
                    "question": question,
                    "document_id": document_id,
                    "source_type": source_type,
                    "expected_answer": expected_answer,
                    "generated_answer": generated_answer,
                    "reference_chunk_ids": reference_chunk_ids,
                    "predicted_chunk_ids": predicted_chunk_ids,
                    "citation_evaluation": citation_evaluation,
                    "judge_evaluation": judge_evaluation,
                    "sources": sources
                }
            )

        summary = self._build_summary(results=results)

        return {
            "total_questions": len(results),
            "top_k": top_k,
            "summary": summary,
            "results": results
        }

    def _extract_source_chunk_ids(
        self,
        sources: list[dict]
    ) -> list[int]:

        chunk_ids = []

        for source in sources:
            chunk_id = source.get("chunk_id")

            if chunk_id is not None:
                chunk_ids.append(int(chunk_id))

        return chunk_ids

    def _evaluate_citation_support(
        self,
        predicted_chunk_ids: list[int],
        reference_chunk_ids: list[int]
    ) -> dict:

        if not reference_chunk_ids:
            return {
                "citation_hit": 0,
                "citation_recall": 0.0,
                "matched_chunk_ids": []
            }

        predicted_set = set(predicted_chunk_ids)
        reference_set = set(reference_chunk_ids)

        matched_chunk_ids = list(
            predicted_set.intersection(reference_set)
        )

        citation_hit = 1 if matched_chunk_ids else 0

        citation_recall = round(
            len(matched_chunk_ids) / len(reference_set),
            4
        )

        return {
            "citation_hit": citation_hit,
            "citation_recall": citation_recall,
            "matched_chunk_ids": matched_chunk_ids
        }

    def _build_summary(
        self,
        results: list[dict]
    ) -> dict:

        if not results:
            return {
                "average_citation_hit": 0.0,
                "average_citation_recall": 0.0,
                "average_correctness_score": 0.0,
                "average_faithfulness_score": 0.0,
                "average_relevance_score": 0.0,
                "hallucination_rate": 0.0
            }

        total_citation_hit = 0
        total_citation_recall = 0.0

        total_correctness = 0.0
        total_faithfulness = 0.0
        total_relevance = 0.0
        hallucination_count = 0

        for result in results:
            citation_evaluation = result["citation_evaluation"]
            judge_evaluation = result["judge_evaluation"]

            total_citation_hit += citation_evaluation["citation_hit"]
            total_citation_recall += citation_evaluation["citation_recall"]

            total_correctness += float(
                judge_evaluation.get("correctness_score", 0.0)
            )

            total_faithfulness += float(
                judge_evaluation.get("faithfulness_score", 0.0)
            )

            total_relevance += float(
                judge_evaluation.get("relevance_score", 0.0)
            )

            if judge_evaluation.get("hallucination") is True:
                hallucination_count += 1

        total_questions = len(results)

        return {
            "average_citation_hit": round(total_citation_hit / total_questions, 4),
            "average_citation_recall": round(total_citation_recall / total_questions, 4),
            "average_correctness_score": round(total_correctness / total_questions, 4),
            "average_faithfulness_score": round(total_faithfulness / total_questions, 4),
            "average_relevance_score": round(total_relevance / total_questions, 4),
            "hallucination_rate": round(hallucination_count / total_questions, 4)
        }