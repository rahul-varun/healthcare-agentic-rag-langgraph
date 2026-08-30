from app.agents.llm_client import LLMError, generate
from app.config.settings import Settings
from app.prompts.rewriter import REWRITER_SYSTEM_PROMPT, build_rewriter_prompt


async def rewrite_query(query: str, settings: Settings) -> str:
    try:
        rewritten = await generate(build_rewriter_prompt(query), settings, system=REWRITER_SYSTEM_PROMPT)
    except LLMError:
        return query
    return rewritten.strip() or query
