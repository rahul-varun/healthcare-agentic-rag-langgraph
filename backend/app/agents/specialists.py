from app.agents.llm_client import LLMError, generate
from app.config.settings import Settings

_SPECIALIST_PROMPTS = {
    "clinical_info": """You are the Clinical Information Agent. Summarize only clinically
supported information in the evidence: condition, symptoms, assessment, red flags,
and general management. Do not diagnose the user. Do not invent missing facts.
Return concise notes for a final medical assistant; cite evidence markers when useful.""",
    "medication_safety": """You are the Medication Safety Agent. Extract medication names,
uses, warnings, contraindications, interactions, and dosing caveats from the evidence.
Never prescribe, select a medicine for this individual, or invent a dose. If the evidence
does not establish a medication or dose, say that explicitly. Recommend clinician or
pharmacist confirmation for treatment decisions.""",
    "web_evidence": """You are the Web Evidence Review Agent. Review web-sourced evidence for
recency, authority, and direct relevance. Prefer government, WHO, hospital, and peer-
reviewed sources. Identify conflicts or weak sources and do not treat search snippets as
proof. Return only evidence-grounded notes for the final answer.""",
}


def _evidence_text(evidence: list[dict]) -> str:
    return "\n\n".join(f"[{i}] {item.get('text', '')}" for i, item in enumerate(evidence, start=1))


async def run_specialist(name: str, query: str, evidence: list[dict], settings: Settings) -> str:
    if not evidence:
        return "No evidence available for this specialist review."
    prompt = f"Question: {query}\n\nEvidence:\n{_evidence_text(evidence)}"
    try:
        return await generate(prompt, settings, system=_SPECIALIST_PROMPTS[name])
    except LLMError as exc:
        return f"Specialist review unavailable: {exc}"
