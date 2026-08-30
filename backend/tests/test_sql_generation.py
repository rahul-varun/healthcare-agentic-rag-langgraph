from app.agents.sql_generation import parse_sql_response


def test_parses_plain_sql():
    assert parse_sql_response("SELECT * FROM companies") == "SELECT * FROM companies"


def test_strips_code_fences():
    assert parse_sql_response("```sql\nSELECT 1\n```") == "SELECT 1"


def test_none_response_returns_none():
    assert parse_sql_response("NONE") is None
    assert parse_sql_response("none") is None


def test_empty_response_returns_none():
    assert parse_sql_response("   ") is None
