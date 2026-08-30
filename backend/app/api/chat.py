import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.agents.graph_definition import run_agent
from app.agents.llm_client import LLMError
from app.observability.metrics import get_metrics_registry
from app.security.auth import require_api_key
from app.security.cache import get_response_cache
from app.security.rate_limit import enforce_rate_limit

router = APIRouter(tags=["chat"], dependencies=[Depends(require_api_key), Depends(enforce_rate_limit)])


class ChatRequest(BaseModel):
    query: str
    top_k: int = 5
    filters: dict | None = None
    response_language: str = "english"


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict] = []
    intent: str | None = None
    tool_calls: list[str] = []
    errors: list[str] = []
    output_policy: str | None = None
    trace: list[dict] = []


def _cache_key(request: ChatRequest) -> str:
    payload = json.dumps(
        {
            "query": request.query,
            "top_k": request.top_k,
            "filters": request.filters,
            "response_language": request.response_language,
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    registry = get_metrics_registry()
    cache = get_response_cache()
    cache_key = _cache_key(request)

    cached = cache.get(cache_key)
    if cached is not None:
        registry.record_request()
        return ChatResponse(**cached)

    registry.record_request()
    try:
        state = await run_agent(
            request.query,
            top_k=request.top_k,
            filters=request.filters,
            response_language=request.response_language,
        )
    except LLMError as exc:
        registry.record_error()
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    registry.record_tool_calls(state.get("tool_calls", []))
    answer = state.get("final_answer") or state.get("draft_answer") or ""
    sources = [item.get("metadata", {}) for item in state.get("evidence", [])]
    response = ChatResponse(
        answer=answer,
        sources=sources,
        intent=state.get("intent"),
        tool_calls=state.get("tool_calls", []),
        errors=state.get("errors", []),
        output_policy=state.get("output_policy"),
        trace=state.get("trace", []),
    )
    cache.set(cache_key, response.model_dump())
    return response
