import asyncio

import httpx
import pytest

from app.agents.llm_client import _post_with_retries


class _FakeResponse:
    def __init__(self, status_code: int):
        self.status_code = status_code


class _FakeClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self.call_count = 0

    async def post(self, url, headers=None, json=None):
        self.call_count += 1
        item = self._responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def test_succeeds_immediately_without_retry():
    client = _FakeClient([_FakeResponse(200)])
    response = asyncio.run(_post_with_retries(client, "url", {}, {}, max_retries=2, base_delay_seconds=0))
    assert response.status_code == 200
    assert client.call_count == 1


def test_retries_on_5xx_then_succeeds():
    client = _FakeClient([_FakeResponse(503), _FakeResponse(200)])
    response = asyncio.run(_post_with_retries(client, "url", {}, {}, max_retries=2, base_delay_seconds=0))
    assert response.status_code == 200
    assert client.call_count == 2


def test_exhausts_retries_and_returns_last_failure():
    client = _FakeClient([_FakeResponse(500), _FakeResponse(500), _FakeResponse(500)])
    response = asyncio.run(_post_with_retries(client, "url", {}, {}, max_retries=2, base_delay_seconds=0))
    assert response.status_code == 500
    assert client.call_count == 3


def test_retries_on_connection_error_then_succeeds():
    client = _FakeClient([httpx.ConnectError("boom"), _FakeResponse(200)])
    response = asyncio.run(_post_with_retries(client, "url", {}, {}, max_retries=2, base_delay_seconds=0))
    assert response.status_code == 200


def test_raises_after_exhausting_retries_on_connection_error():
    client = _FakeClient([httpx.ConnectError("boom"), httpx.ConnectError("boom"), httpx.ConnectError("boom")])
    with pytest.raises(httpx.ConnectError):
        asyncio.run(_post_with_retries(client, "url", {}, {}, max_retries=2, base_delay_seconds=0))


def test_does_not_retry_non_retryable_status():
    client = _FakeClient([_FakeResponse(401)])
    response = asyncio.run(_post_with_retries(client, "url", {}, {}, max_retries=2, base_delay_seconds=0))
    assert response.status_code == 401
    assert client.call_count == 1
