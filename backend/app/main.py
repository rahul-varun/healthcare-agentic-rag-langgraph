import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, documents, evaluation, graph, health, metrics
from app.config.settings import get_settings
from app.observability.logging_config import configure_logging

configure_logging()
logger = logging.getLogger("app.request")

_settings = get_settings()
if not _settings.openrouter_api_key or _settings.openrouter_api_key == "your_key":
    logging.getLogger("app.startup").warning(
        "OPENROUTER_API_KEY is not configured (empty or placeholder) — LLM-dependent calls will fail"
    )

app = FastAPI(title="HealthAgent AI Healthcare Knowledge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_allowed_origins.split(",") if _settings.cors_allowed_origins else [],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(graph.router)
app.include_router(evaluation.router)
app.include_router(metrics.router)
app.include_router(documents.router)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "request completed",
        extra={
            "extra_fields": {
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response
