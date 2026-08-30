from app.agents.evidence_check import parse_verification


def test_parses_unsupported_claims():
    raw = '{"unsupported_claims": ["Revenue grew 50%"]}'
    assert parse_verification(raw) == ["Revenue grew 50%"]


def test_empty_claims_list():
    assert parse_verification('{"unsupported_claims": []}') == []


def test_invalid_json_returns_empty_list():
    assert parse_verification("not json") == []


def test_wrong_shape_returns_empty_list():
    assert parse_verification('["not", "a", "dict"]') == []


def test_non_list_claims_field_returns_empty_list():
    assert parse_verification('{"unsupported_claims": "not a list"}') == []
