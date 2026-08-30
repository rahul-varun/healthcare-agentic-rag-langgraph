from app.guardrails.pii import detect_pii, redact_pii
from app.guardrails.medical_safety import needs_medical_safety_note

# SAFE / UNSAFE / NEEDS_REVIEW policy vocabulary per skills.md section 10.
# Full output guardrails (unsafe content classification, hallucinated-citation
# detection, structured-output validation) are broader than what's implemented
# here — this acts on what Phase 4's evidence check already produces (unsupported
# claims) plus PII leakage, per section 10's own example checks.


def classify_output_safety(draft_answer: str, verification: dict | None) -> str:
    if detect_pii(draft_answer):
        return "UNSAFE"
    if verification and verification.get("checked") and verification.get("unsupported_claims"):
        return "NEEDS_REVIEW"
    if needs_medical_safety_note(draft_answer):
        return "NEEDS_REVIEW"
    return "SAFE"


def apply_output_guardrail(draft_answer: str, verification: dict | None) -> tuple[str, str]:
    policy = classify_output_safety(draft_answer, verification)

    if policy == "UNSAFE":
        return redact_pii(draft_answer), policy

    if policy == "NEEDS_REVIEW":
        unsupported = (verification or {}).get("unsupported_claims") or []
        caveat = ""
        if unsupported:
            caveat += (
                "\n\nNote: the following statements could not be verified against the "
                "retrieved evidence: " + "; ".join(unsupported)
            )
        if needs_medical_safety_note(draft_answer):
            caveat += (
                "\n\nMedical safety note: This is general educational information, "
                "not a diagnosis or prescription. Confirm treatment, dosage, and "
                "urgent symptoms with a qualified healthcare professional."
            )
        return draft_answer + caveat, policy

    return draft_answer, policy
