import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.evaluation.runner import evaluate_retrieval, load_eval_dataset
from app.retrieval.retriever import get_retriever
from app.security.auth import require_api_key

router = APIRouter(tags=["evaluation"], dependencies=[Depends(require_api_key)])

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DATASET_PATH = _REPO_ROOT / "evaluation" / "datasets" / "smoke_questions.json"
_REPORTS_DIR = _REPO_ROOT / "evaluation" / "reports"
_LATEST_PATH = _REPORTS_DIR / "latest_retrieval_eval.json"


class EvaluationResponse(BaseModel):
    aggregate: dict
    per_question: list[dict]
    n_questions: int


@router.post("/api/evaluation/run", response_model=EvaluationResponse)
async def run_evaluation() -> EvaluationResponse:
    if not _DATASET_PATH.exists():
        raise HTTPException(status_code=400, detail=f"No evaluation dataset at {_DATASET_PATH}")
    dataset = load_eval_dataset(_DATASET_PATH)

    retriever = get_retriever()

    def retrieve_fn(question: str, top_k: int) -> list[dict]:
        return [{"metadata": chunk.metadata} for chunk in retriever.retrieve(question, top_k=top_k)]

    result = evaluate_retrieval(dataset, retrieve_fn)
    _REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    _LATEST_PATH.write_text(json.dumps(result, indent=2))
    return EvaluationResponse(**result)


@router.get("/api/evaluation/results", response_model=EvaluationResponse)
async def get_evaluation_results() -> EvaluationResponse:
    if not _LATEST_PATH.exists():
        raise HTTPException(status_code=404, detail="No evaluation has been run yet — POST /api/evaluation/run first")
    return EvaluationResponse(**json.loads(_LATEST_PATH.read_text()))
