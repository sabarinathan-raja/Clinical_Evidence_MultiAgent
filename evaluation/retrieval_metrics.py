
def precision_at_k(retrieved, relevant, k=5):

    retrieved = retrieved[:k]

    if not retrieved:
        return 0.0

    relevant_set = set(relevant)

    hits = sum(
        1 for item in retrieved
        if item in relevant_set
    )

    return hits / len(retrieved)


def recall_at_k(retrieved, relevant, k=5):

    relevant_set = set(relevant)

    if not relevant_set:
        return 0.0

    hits = sum(
        1 for item in retrieved[:k]
        if item in relevant_set
    )

    return hits / len(relevant_set)


def reciprocal_rank(retrieved, relevant):

    relevant_set = set(relevant)

    for rank, item in enumerate(retrieved, start=1):

        if item in relevant_set:
            return 1.0 / rank

    return 0.0


def mean_reciprocal_rank(results):

    if not results:
        return 0.0

    scores = [
        reciprocal_rank(
            item["retrieved"],
            item["relevant"]
        )
        for item in results
    ]

    return sum(scores) / len(scores)


def evaluate_retrieval(
    retrieved,
    relevant,
    k=5
):

    return {
        "precision_at_k": precision_at_k(
            retrieved, relevant, k
        ),
        "recall_at_k": recall_at_k(
            retrieved, relevant, k
        ),
        "reciprocal_rank": reciprocal_rank(
            retrieved, relevant
        )
    }
