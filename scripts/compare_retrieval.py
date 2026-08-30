#!/usr/bin/env python3
"""Compare basic vector retrieval vs. hybrid+reranked retrieval on the smoke
evaluation dataset (skills.md section 14: 'Compare Multiple RAG Versions').

IMPORTANT: this runs against evaluation/datasets/smoke_questions.json, which is
answerable only from the single placeholder document currently in
knowledge_base/. The numbers below are real (not fabricated) but not
statistically meaningful — a real comparison needs 50-100 questions against
real documents, per skills.md section 13.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.evaluation.runner import evaluate_retrieval, load_eval_dataset  # noqa: E402
from app.retrieval.retriever import get_retriever  # noqa: E402

DATASET_PATH = Path(__file__).resolve().parent.parent / "evaluation" / "datasets" / "smoke_questions.json"


def main() -> None:
    dataset = load_eval_dataset(DATASET_PATH)
    if not dataset:
        print(f"No questions found at {DATASET_PATH}")
        return

    retriever = get_retriever()

    versions = {
        "A: Basic Vector RAG (dense only)": lambda q, k: [
            {"metadata": c.metadata} for c in retriever.retrieve_dense_only(q, top_k=k)
        ],
        "C: Hybrid + Reranker": lambda q, k: [{"metadata": c.metadata} for c in retriever.retrieve(q, top_k=k)],
    }

    print(f"Evaluated on {len(dataset)} questions from {DATASET_PATH.name}\n")
    header = f"{'Version':<35} {'HitRate':>8} {'MRR':>8} {'Recall':>8} {'NDCG':>8}"
    print(header)
    print("-" * len(header))
    for name, retrieve_fn in versions.items():
        result = evaluate_retrieval(dataset, retrieve_fn)
        agg = result["aggregate"]
        print(
            f"{name:<35} {agg['hit_rate']:>8.2f} {agg['reciprocal_rank']:>8.2f} "
            f"{agg['recall_at_k']:>8.2f} {agg['ndcg_at_k']:>8.2f}"
        )

    print(
        "\nNote: measured on a tiny smoke dataset against one placeholder document — "
        "useful to confirm the harness works, not a statistically meaningful benchmark."
    )


if __name__ == "__main__":
    main()
