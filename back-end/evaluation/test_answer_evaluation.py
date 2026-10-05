from pathlib import Path

from core.database import SessionLocal
from evaluation.services.answer_evaluation_service import AnswerEvaluationService


def main():
    db = SessionLocal()

    try:
        dataset_path = (
            Path(__file__).resolve().parent
            / "datasets"
            / "rag_eval_dataset.json"
        )

        service = AnswerEvaluationService()

        result = service.evaluate_dataset(
            db=db,
            dataset_path=str(dataset_path),
            top_k=5
        )

        print("TOTAL QUESTIONS:")
        print(result["total_questions"])

        print("\nSUMMARY:")
        print(result["summary"])

        print("\nQUESTION RESULTS:")
        for item in result["results"]:
            print("\n----------------------------")
            print("QUESTION:")
            print(item["question"])

            print("\nEXPECTED ANSWER:")
            print(item["expected_answer"])

            print("\nGENERATED ANSWER:")
            print(item["generated_answer"])

            print("\nREFERENCE CHUNK IDS:")
            print(item["reference_chunk_ids"])

            print("\nPREDICTED CHUNK IDS:")
            print(item["predicted_chunk_ids"])

            print("\nCITATION EVALUATION:")
            print(item["citation_evaluation"])

    finally:
        db.close()


if __name__ == "__main__":
    main()