import httpx

from app.config.settings import Settings

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


class WebSearchError(RuntimeError):
    pass


def _allowed_domains(settings: Settings) -> list[str]:
    raw = settings.web_search_allowed_domains.strip()
    return [d.strip().lower() for d in raw.split(",") if d.strip()] if raw else []


def _is_allowed(url: str, allowed_domains: list[str]) -> bool:
    if not allowed_domains:
        return True
    return any(domain in url.lower() for domain in allowed_domains)


async def search_web(query: str, settings: Settings) -> list[dict]:
    if not settings.tavily_api_key:
        raise WebSearchError("TAVILY_API_KEY is not set")

    try:
        async with httpx.AsyncClient(timeout=settings.web_search_timeout_seconds) as client:
            response = await client.post(
                TAVILY_SEARCH_URL,
                json={
                    "api_key": settings.tavily_api_key,
                    "query": query,
                    "max_results": settings.web_search_max_results,
                },
            )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise WebSearchError(f"Web search request failed: {exc.response.status_code} {exc.response.text}") from exc
    except httpx.RequestError as exc:
        raise WebSearchError(f"Web search request failed: {exc}") from exc

    allowed_domains = _allowed_domains(settings)
    data = response.json()
    results = []
    for item in data.get("results", []):
        url = item.get("url", "")
        if not _is_allowed(url, allowed_domains):
            continue
        content = (item.get("content") or "")[: settings.web_search_max_content_chars]
        results.append({"title": item.get("title", ""), "url": url, "content": content})
    return results
