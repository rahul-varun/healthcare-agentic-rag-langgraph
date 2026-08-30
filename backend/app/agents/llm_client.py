import asyncio

import httpx

from app.config.settings import Settings
from app.observability.metrics import get_metrics_registry

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class LLMError(RuntimeError):
    pass


async def _post_with_retries(
    client: httpx.AsyncClient,
    url: str,
    headers: dict,
    json_body: dict,
    max_retries: int,
    base_delay_seconds: float,
) -> httpx.Response:
    """Retries on transient failures (429/5xx, connection errors) with
    exponential backoff. Non-retryable errors (e.g. 401) return immediately."""
    last_exc: httpx.RequestError | None = None
    for attempt in range(max_retries + 1):
        try:
            response = await client.post(url, headers=headers, json=json_body)
        except httpx.RequestError as exc:
            last_exc = exc
            if attempt < max_retries:
                await asyncio.sleep(base_delay_seconds * (2**attempt))
                continue
            raise
        if response.status_code in _RETRYABLE_STATUS_CODES and attempt < max_retries:
            await asyncio.sleep(base_delay_seconds * (2**attempt))
            continue
        return response
    raise last_exc  # pragma: no cover — loop above always returns or raises


async def generate(prompt: str, settings: Settings, system: str | None = None) -> str:
    if settings.llm_provider != "openrouter":
        raise LLMError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
    if not settings.openrouter_api_key:
        raise LLMError("OPENROUTER_API_KEY is not set")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await _post_with_retries(
                client,
                OPENROUTER_CHAT_URL,
                headers={"Authorization": f"Bearer {settings.openrouter_api_key}"},
                json_body={"model": settings.llm_model, "messages": messages},
                max_retries=settings.llm_max_retries,
                base_delay_seconds=settings.llm_retry_base_delay_seconds,
            )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise LLMError(f"OpenRouter request failed: {exc.response.status_code} {exc.response.text}") from exc
    except httpx.RequestError as exc:
        raise LLMError(f"OpenRouter request failed: {exc}") from exc

    data = response.json()
    usage = data.get("usage") or {}
    get_metrics_registry().record_llm_usage(usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0))
    return data["choices"][0]["message"]["content"]
