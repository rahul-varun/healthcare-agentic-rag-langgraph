SQL_SCHEMA_DESCRIPTION = """
Tables:
  health_plans(id, name, insurer, country)
  benefits(id, health_plan_id, benefit, coverage_limit, waiting_period, source_document, source_page)
  claims(id, member_id, benefit, status, amount, submitted_at, source_document, source_page)
"""

SQL_SYSTEM_PROMPT = f"""You translate a health-card or healthcare question into a single read-only
PostgreSQL SELECT statement against this schema:
{SQL_SCHEMA_DESCRIPTION}
Rules:
- Output ONLY the SQL statement, nothing else — no markdown fences, no explanation.
- SELECT statements only. Never write INSERT/UPDATE/DELETE/DROP/ALTER or any other
  data-modifying statement.
- If the question cannot be answered from this schema, output exactly: NONE"""


def build_sql_prompt(question: str) -> str:
    return f"Question: {question}"
