import time

from app.security.rate_limit import RateLimiter


def test_allows_requests_within_limit():
    limiter = RateLimiter(max_requests=3, window_seconds=10)
    assert limiter.allow("client-a") is True
    assert limiter.allow("client-a") is True
    assert limiter.allow("client-a") is True


def test_blocks_requests_over_limit():
    limiter = RateLimiter(max_requests=2, window_seconds=10)
    assert limiter.allow("client-a") is True
    assert limiter.allow("client-a") is True
    assert limiter.allow("client-a") is False


def test_different_clients_have_independent_limits():
    limiter = RateLimiter(max_requests=1, window_seconds=10)
    assert limiter.allow("client-a") is True
    assert limiter.allow("client-b") is True


def test_window_resets_after_expiry():
    limiter = RateLimiter(max_requests=1, window_seconds=0.05)
    assert limiter.allow("client-a") is True
    assert limiter.allow("client-a") is False
    time.sleep(0.1)
    assert limiter.allow("client-a") is True
