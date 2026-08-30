VALID_INTENTS = {"factual", "calculation", "relationship", "explanation", "complex_research"}

CLASSIFIER_SYSTEM_PROMPT = f"""Classify the user's healthcare or health-card question into exactly one of these
intents: {sorted(VALID_INTENTS)}

- factual: coverage, eligibility, limits, documents, or claim-status lookup
- calculation: needs arithmetic, such as remaining coverage or reimbursement
- relationship: connects a benefit, treatment, hospital, insurer, or policy
- explanation: asks why/how a claim or benefit rule works
- complex_research: needs multiple policy or healthcare sources combined

Output ONLY the single intent word, nothing else."""


def build_classifier_prompt(query: str) -> str:
    return f"Question: {query}"


def parse_intent(raw: str) -> str | None:
    text = raw.strip().lower()
    for intent in VALID_INTENTS:
        if intent in text:
            return intent
    return None
