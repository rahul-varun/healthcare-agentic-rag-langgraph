import pytest

from app.tools.sql_tool import SQLGuardError, enforce_row_limit, validate_select_only


def test_select_passes():
    validate_select_only("SELECT * FROM financials")


def test_case_insensitive_select_passes():
    validate_select_only("  select name from companies")


def test_rejects_non_select():
    with pytest.raises(SQLGuardError):
        validate_select_only("UPDATE financials SET value = 0")


def test_rejects_forbidden_keyword_even_in_select_shaped_query():
    with pytest.raises(SQLGuardError):
        validate_select_only("SELECT * FROM financials; DROP TABLE financials;")


def test_rejects_multiple_statements():
    with pytest.raises(SQLGuardError):
        validate_select_only("SELECT 1; SELECT 2")


def test_rejects_empty_query():
    with pytest.raises(SQLGuardError):
        validate_select_only("   ")


def test_forbidden_keyword_as_substring_of_column_name_is_not_falsely_blocked():
    # "updated_at" contains "update" as a substring but not as a whole word
    validate_select_only("SELECT updated_at FROM financials")


def test_enforce_row_limit_appends_when_missing():
    assert enforce_row_limit("SELECT * FROM financials", 50) == "SELECT * FROM financials LIMIT 50"


def test_enforce_row_limit_leaves_existing_limit_untouched():
    query = "SELECT * FROM financials LIMIT 10"
    assert enforce_row_limit(query, 50) == query
