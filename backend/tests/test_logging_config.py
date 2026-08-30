import json
import logging

from app.observability.logging_config import JsonFormatter


def test_json_formatter_produces_valid_json_with_expected_fields():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="app.request", level=logging.INFO, pathname="", lineno=0, msg="hello", args=(), exc_info=None
    )
    output = formatter.format(record)
    payload = json.loads(output)
    assert payload["message"] == "hello"
    assert payload["level"] == "INFO"
    assert payload["logger"] == "app.request"


def test_json_formatter_includes_extra_fields():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="app.request", level=logging.INFO, pathname="", lineno=0, msg="hello", args=(), exc_info=None
    )
    record.extra_fields = {"request_id": "abc-123", "status_code": 200}
    payload = json.loads(formatter.format(record))
    assert payload["request_id"] == "abc-123"
    assert payload["status_code"] == 200
