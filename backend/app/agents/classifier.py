from app.agents.llm_client import LLMError, generate
from app.config.settings import Settings
from app.prompts.classifier import CLASSIFIER_SYSTEM_PROMPT, build_classifier_prompt, parse_intent

_KEYWORD_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("calculation", ("growth rate", "percentage", "% ", "calculate")),
    ("relationship", ("connected to", "relationship", "competitor", "acquired")),
    ("explanation", ("why ", "reason", "cause", "decline", "increase")),
    ("complex_research", (" and ", "compare", "analysts")),
]


def fallback_classify(query: str) -> str:
    lowered = query.lower()
    for intent, keywords in _KEYWORD_RULES:
        if any(keyword in lowered for keyword in keywords):
            return intent
    return "factual"


async def classify_intent(query: str, settings: Settings) -> str:
    try:
        raw = await generate(build_classifier_prompt(query), settings, system=CLASSIFIER_SYSTEM_PROMPT)
    except LLMError:
        return fallback_classify(query)
    return parse_intent(raw) or fallback_classify(query)
