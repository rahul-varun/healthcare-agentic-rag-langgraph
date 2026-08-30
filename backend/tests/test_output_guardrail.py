from app.guardrails.output_guardrail import apply_output_guardrail, classify_output_safety


def test_no_verification_passes_through_unchanged():
    text, policy = apply_output_guardrail("The answer.", None)
    assert text == "The answer."
    assert policy == "SAFE"


def test_unchecked_verification_passes_through_unchanged():
    text, policy = apply_output_guardrail("The answer.", {"checked": False})
    assert text == "The answer."
    assert policy == "SAFE"


def test_no_unsupported_claims_passes_through_unchanged():
    verification = {"checked": True, "unsupported_claims": []}
    text, policy = apply_output_guardrail("The answer.", verification)
    assert text == "The answer."
    assert policy == "SAFE"


def test_unsupported_claims_appended_as_caveat():
    verification = {"checked": True, "unsupported_claims": ["Revenue grew 50%"]}
    text, policy = apply_output_guardrail("The answer.", verification)
    assert text.startswith("The answer.")
    assert "Revenue grew 50%" in text
    assert policy == "NEEDS_REVIEW"


def test_pii_in_answer_is_redacted_and_marked_unsafe():
    draft = "Contact the CFO at cfo@example.com for details."
    text, policy = apply_output_guardrail(draft, None)
    assert policy == "UNSAFE"
    assert "cfo@example.com" not in text
    assert "[REDACTED_EMAIL]" in text


def test_pii_takes_priority_over_unsupported_claims():
    draft = "Reach out to cfo@example.com. Revenue grew 50%."
    verification = {"checked": True, "unsupported_claims": ["Revenue grew 50%"]}
    _, policy = apply_output_guardrail(draft, verification)
    assert policy == "UNSAFE"


def test_classify_output_safety_matches_apply_output_guardrail():
    assert classify_output_safety("clean answer", None) == "SAFE"
