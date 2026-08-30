import time

from app.security.cache import TTLCache


def test_set_and_get():
    cache = TTLCache(ttl_seconds=10)
    cache.set("key", {"value": 42})
    assert cache.get("key") == {"value": 42}


def test_missing_key_returns_none():
    cache = TTLCache(ttl_seconds=10)
    assert cache.get("missing") is None


def test_expired_entry_returns_none():
    cache = TTLCache(ttl_seconds=0.05)
    cache.set("key", "value")
    time.sleep(0.1)
    assert cache.get("key") is None


def test_evicts_oldest_when_over_capacity():
    cache = TTLCache(ttl_seconds=10, max_size=2)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    assert len(cache._store) == 2
    assert cache.get("c") == 3
