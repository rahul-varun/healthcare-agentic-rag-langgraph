import re
from functools import lru_cache

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.config.settings import get_settings

# skills.md section 11: read-only user, SELECT only, block DDL/DML, query
# timeout, row limits, statement validation. The DB-level read-only role has to
# be provisioned on the actual Postgres instance (out of this codebase's
# control) — this is the application-level half of that defense.
_FORBIDDEN_KEYWORDS = (
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "GRANT",
    "REVOKE",
    "EXEC",
    "EXECUTE",
    "MERGE",
    "ATTACH",
    "PRAGMA",
    "COPY",
    "CALL",
    "VACUUM",
)
_FORBIDDEN_RE = re.compile(r"\b(" + "|".join(_FORBIDDEN_KEYWORDS) + r")\b", re.IGNORECASE)
_LIMIT_RE = re.compile(r"\blimit\b", re.IGNORECASE)


class SQLGuardError(RuntimeError):
    pass


class SQLExecutionError(RuntimeError):
    pass


def validate_select_only(query: str) -> None:
    stripped = query.strip().rstrip(";")
    if not stripped:
        raise SQLGuardError("Empty query")
    if ";" in stripped:
        raise SQLGuardError("Multiple statements are not allowed")
    if not re.match(r"^\s*SELECT\b", stripped, re.IGNORECASE):
        raise SQLGuardError("Only SELECT statements are allowed")
    if _FORBIDDEN_RE.search(stripped):
        raise SQLGuardError("Query contains a forbidden keyword")


def enforce_row_limit(query: str, max_rows: int) -> str:
    stripped = query.strip().rstrip(";")
    if _LIMIT_RE.search(stripped):
        return stripped
    return f"{stripped} LIMIT {max_rows}"


@lru_cache
def _get_engine():
    settings = get_settings()
    return create_engine(settings.postgres_url)


def check_connection() -> bool:
    try:
        with _get_engine().connect():
            return True
    except SQLAlchemyError:
        return False


def query_sql(query: str, max_rows: int = 100, timeout_seconds: int = 10) -> list[dict]:
    validate_select_only(query)
    safe_query = enforce_row_limit(query, max_rows)

    try:
        engine = _get_engine()
        with engine.connect() as connection:
            connection.execute(text(f"SET LOCAL statement_timeout = '{int(timeout_seconds * 1000)}'"))
            result = connection.execute(text(safe_query))
            return [dict(row._mapping) for row in result]
    except SQLAlchemyError as exc:
        raise SQLExecutionError(f"SQL query failed: {exc}") from exc
