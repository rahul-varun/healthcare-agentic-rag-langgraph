import time
from functools import lru_cache
from threading import Lock
from typing import Any

from app.config.settings import get_settings


class TTLCache:
    """In-memory TTL cache — a demo-scale response cache, not a Redis-backed
    production one (which is what a multi-instance deployment would need)."""

    def __init__(self, ttl_seconds: float, max_size: int = 256):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if time.monotonic() > expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if len(self._store) >= self.max_size and key not in self._store:
                oldest_key = min(self._store, key=lambda k: self._store[k][0])
                del self._store[oldest_key]
            self._store[key] = (time.monotonic() + self.ttl_seconds, value)


@lru_cache
def get_response_cache() -> TTLCache:
    settings = get_settings()
    return TTLCache(ttl_seconds=settings.cache_ttl_seconds)
