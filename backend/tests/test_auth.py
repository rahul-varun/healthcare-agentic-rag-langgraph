import pytest
from fastapi import HTTPException

from app.security import auth


class _FakeSettings:
    def __init__(self, api_key: str):
        self.api_key = api_key


def test_auth_disabled_when_no_api_key_configured(monkeypatch):
    monkeypatch.setattr(auth, "get_settings", lambda: _FakeSettings(api_key=""))
    import asyncio

    asyncio.run(auth.require_api_key(x_api_key=None))  # must not raise


def test_correct_api_key_passes(monkeypatch):
    monkeypatch.setattr(auth, "get_settings", lambda: _FakeSettings(api_key="secret123"))
    import asyncio

    asyncio.run(auth.require_api_key(x_api_key="secret123"))  # must not raise


def test_missing_api_key_rejected(monkeypatch):
    monkeypatch.setattr(auth, "get_settings", lambda: _FakeSettings(api_key="secret123"))
    import asyncio

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(auth.require_api_key(x_api_key=None))
    assert exc_info.value.status_code == 401


def test_wrong_api_key_rejected(monkeypatch):
    monkeypatch.setattr(auth, "get_settings", lambda: _FakeSettings(api_key="secret123"))
    import asyncio

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(auth.require_api_key(x_api_key="wrong"))
    assert exc_info.value.status_code == 401
