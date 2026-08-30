import re

from app.agents.llm_client import LLMError, generate
from app.config.settings import Settings
from app.prompts.sql import SQL_SYSTEM_PROMPT, build_sql_prompt

_CODE_FENCE_RE = re.compile(r"^```(?:\w+)?\s*|\s*```$")


def parse_sql_response(raw: str) -> str | None:
    text = _CODE_FENCE_RE.sub("", raw.strip()).strip()
    if not text or text.upper() == "NONE":
        return None
    return text


async def generate_sql(question: str, settings: Settings) -> str | None:
    try:
        raw = await generate(build_sql_prompt(question), settings, system=SQL_SYSTEM_PROMPT)
    except LLMError:
        return None
    return parse_sql_response(raw)
