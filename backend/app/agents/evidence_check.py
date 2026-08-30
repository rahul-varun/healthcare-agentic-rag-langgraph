from app.agents.llm_client import LLMError, generate
from app.agents.llm_json import parse_json_object
from app.config.settings import Settings
from app.prompts.evidence_check import EVIDENCE_CHECK_SYSTEM_PROMPT, build_evidence_check_prompt


def parse_verification(raw: str) -> list[str]:
    data = parse_json_object(raw)
    if not isinstance(data, dict):
        return []
    claims = data.get("unsupported_claims")
    if not isinstance(claims, list):
        return []
    return [str(claim) for claim in claims if str(claim).strip()]


async def verify_claims(draft_answer: str, evidence: list[dict], settings: Settings) -> dict:
    if not evidence:
        return {"checked": False, "reason": "no evidence to verify against"}
    prompt = build_evidence_check_prompt(draft_answer, evidence)
    try:
        raw = await generate(prompt, settings, system=EVIDENCE_CHECK_SYSTEM_PROMPT)
    except LLMError as exc:
        return {"checked": False, "reason": str(exc)}
    return {"checked": True, "unsupported_claims": parse_verification(raw)}
