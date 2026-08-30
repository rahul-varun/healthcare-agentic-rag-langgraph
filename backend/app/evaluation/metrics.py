import math


def hit_rate(relevances: list[bool]) -> float:
    return 1.0 if any(relevances) else 0.0


def reciprocal_rank(relevances: list[bool]) -> float:
    for i, is_relevant in enumerate(relevances, start=1):
        if is_relevant:
            return 1.0 / i
    return 0.0


def recall_at_k(relevances: list[bool], total_relevant: int) -> float:
    if total_relevant == 0:
        return 0.0
    return sum(relevances) / total_relevant


def precision_at_k(relevances: list[bool]) -> float:
    if not relevances:
        return 0.0
    return sum(relevances) / len(relevances)


def ndcg_at_k(relevances: list[bool], ideal_relevant_count: int | None = None) -> float:
    """Binary-relevance NDCG. With exactly one relevant item (this project's
    smoke dataset), this reduces to 1/log2(rank+1) when found, else 0."""
    if ideal_relevant_count is None:
        ideal_relevant_count = sum(relevances)
    dcg = sum(1.0 / math.log2(i + 1) for i, is_relevant in enumerate(relevances, start=1) if is_relevant)
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, ideal_relevant_count + 1))
    return dcg / idcg if idcg > 0 else 0.0
