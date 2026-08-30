from app.guardrails.pii import detect_pii, redact_pii


def test_detects_email():
    assert "email" in detect_pii("Contact me at jane.doe@example.com")


def test_detects_ssn():
    assert "ssn" in detect_pii("SSN: 123-45-6789")


def test_detects_grouped_credit_card():
    assert "credit_card" in detect_pii("Card: 4111 1111 1111 1111")


def test_detects_contiguous_credit_card():
    assert "credit_card" in detect_pii("Card number 4111111111111111 on file")


def test_detects_phone_number():
    assert "phone" in detect_pii("Call me at 555-123-4567")


def test_clean_text_has_no_pii():
    assert detect_pii("Why did revenue decline in Q3?") == []


def test_redact_email():
    redacted = redact_pii("Contact jane.doe@example.com now")
    assert "jane.doe@example.com" not in redacted
    assert "[REDACTED_EMAIL]" in redacted


def test_redact_ssn():
    redacted = redact_pii("SSN 123-45-6789 on file")
    assert "123-45-6789" not in redacted
    assert "[REDACTED_SSN]" in redacted
