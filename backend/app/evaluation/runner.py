import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from app.evaluation.metrics import hit_rate, ndcg_at_k, recall_at_k, reciprocal_rank


@dataclass
class EvalQuestion:
    question: str
    expected_document: str
    expected_heading_path: list[str] | None = None


def load_eval_dataset(path: Path) -> list[EvalQuestion]:
    data = json.loads(Path(path).read_text())
    return [
        EvalQuestion(
            question=item["question"],
            expected_document=item["expected_document"],
            expected_heading_path=item.get("expected_heading_path"),
        )
        for item in data
    ]


def is_relevant(metadata: dict, expected: EvalQuestion) -> bool:
    document = metadata.get("document") or metadata.get("document_name")
    if document != expected.expected_document:
        return False
    if expected.expected_heading_path is not None:
        return metadata.get("heading_path") == expected.expected_heading_path
    return True


def evaluate_retrieval(
    dataset: list[EvalQuestion],
    retrieve_fn: Callable[[str, int], list[dict]],
    top_k: int = 5,
) -> dict:
    """retrieve_fn(question, top_k) -> list of evidence dicts, each with a 'metadata' key."""
    per_question = []
    for expected in dataset:
        results = retrieve_fn(expected.question, top_k)
        # Retrieval returns chunks, but this smoke benchmark evaluates whether
        # the expected document was found. Deduplicate chunks from the same
        # document so one long PDF cannot inflate recall/NDCG above 1.0.
        seen_documents: set[str] = set()
        relevances: list[bool] = []
        for result in results:
            metadata = result["metadata"]
            document = metadata.get("document") or metadata.get("document_name") or ""
            if document in seen_documents:
                continue
            seen_documents.add(document)
            relevances.append(is_relevant(metadata, expected))
        per_question.append(
            {
                "question": expected.question,
                "hit_rate": hit_rate(relevances),
                "reciprocal_rank": reciprocal_rank(relevances),
                "recall_at_k": recall_at_k(relevances, total_relevant=1),
                "ndcg_at_k": ndcg_at_k(relevances, ideal_relevant_count=1),
            }
        )

    n = len(per_question) or 1
    aggregate = {
        metric: sum(q[metric] for q in per_question) / n
        for metric in ("hit_rate", "reciprocal_rank", "recall_at_k", "ndcg_at_k")
    }
    return {"per_question": per_question, "aggregate": aggregate, "n_questions": len(dataset)}
