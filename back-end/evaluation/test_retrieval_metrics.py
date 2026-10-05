from evaluation.metrics.retrieval_metrics import calculate_retrieval_metrics


predicted_chunk_ids = [84, 85, 82, 90, 91]
reference_chunk_ids = [84]

result = calculate_retrieval_metrics(
    predicted_chunk_ids=predicted_chunk_ids,
    reference_chunk_ids=reference_chunk_ids,
    k=5
)

print(result)