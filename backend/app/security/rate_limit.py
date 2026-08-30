import time
from collections import defaultdict, deque
from functools import lru_cache
from threading import Lock

from fastapi import HTTPException, Request

from app.config.settings import get_settings


class RateLimiter:
    """In-memory sliding-window limiter. Per-process only — a multi-instance
    deployment would need a shared store (Redis) instead."""

    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] > self.window_seconds:
                hits.popleft()
            if len(hits) >= self.max_requests:
                return False
            hits.append(now)
            return True


@lru_cache
def get_rate_limiter() -> RateLimiter:
    settings = get_settings()
    return RateLimiter(settings.rate_limit_max_requests, settings.rate_limit_window_seconds)


async def enforce_rate_limit(request: Request) -> None:
    client_key = request.client.host if request.client else "unknown"
    if not get_rate_limiter().allow(client_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
