from fastapi import APIRouter
from pydantic import BaseModel

from app.config.settings import get_settings
from app.observability.metrics import get_metrics_registry

router = APIRouter(tags=["metrics"])


class MetricsResponse(BaseModel):
    request_count: int
    error_count: int
    total_input_tokens: int
    total_output_tokens: int
    tool_call_counts: dict[str, int]
    estimated_cost_usd: float


@router.get("/api/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    settings = get_settings()
    snapshot = get_metrics_registry().snapshot(
        cost_per_1k_input=settings.llm_cost_per_1k_input_tokens,
        cost_per_1k_output=settings.llm_cost_per_1k_output_tokens,
    )
    return MetricsResponse(**snapshot)
