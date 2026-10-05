def calculate_precision_k(
    predicted_chunk_ids: list[int],
    reference_chunk_ids: list[int],
    k: int
) -> float:

    predicted_top_k = predicted_chunk_ids[:k]

    if not predicted_top_k:
        return 0.0

    reference_set = set(reference_chunk_ids)

    correct_count = 0

    for chunk_id in predicted_top_k:
        if chunk_id in reference_set:
            correct_count += 1

    return round(correct_count / len(predicted_top_k), 4)


def calculate_recall_k(
    predicted_chunk_ids: list[int],
    reference_chunk_ids: list[int],
    k: int
) -> float:

    if not reference_chunk_ids:
        return 0.0

    predicted_top_k = predicted_chunk_ids[:k]

    predicted_set = set(predicted_top_k)
    reference_set = set(reference_chunk_ids)

    correct_found = predicted_set.intersection(reference_set)

    return round(len(correct_found) / len(reference_set), 4)


def calculate_mrr(
    predicted_chunk_ids: list[int],
    reference_chunk_ids: list[int]
) -> float:

    reference_set = set(reference_chunk_ids)

    for index, chunk_id in enumerate(predicted_chunk_ids):
        rank = index + 1

        if chunk_id in reference_set:
            return round(1 / rank, 4)

    return 0.0


def calculate_hit_at_k(
    predicted_chunk_ids: list[int],
    reference_chunk_ids: list[int],
    k: int
) -> int:

    predicted_top_k = predicted_chunk_ids[:k]
    reference_set = set(reference_chunk_ids)

    for chunk_id in predicted_top_k:
        if chunk_id in reference_set:
            return 1

    return 0


def calculate_retrieval_metrics(
    predicted_chunk_ids: list[int],
    reference_chunk_ids: list[int],
    k: int
) -> dict:

    return {
        "precision_at_k": calculate_precision_k(
            predicted_chunk_ids=predicted_chunk_ids,
            reference_chunk_ids=reference_chunk_ids,
            k=k
        ),
        "recall_at_k": calculate_recall_k(
            predicted_chunk_ids=predicted_chunk_ids,
            reference_chunk_ids=reference_chunk_ids,
            k=k
        ),
        "mrr": calculate_mrr(
            predicted_chunk_ids=predicted_chunk_ids,
            reference_chunk_ids=reference_chunk_ids
        ),
        "hit_at_k": calculate_hit_at_k(
            predicted_chunk_ids=predicted_chunk_ids,
            reference_chunk_ids=reference_chunk_ids,
            k=k
        )
    }