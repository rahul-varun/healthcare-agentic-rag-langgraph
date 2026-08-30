import re

# Heuristic regex detection, not a full PII classifier — good enough to catch
# the textbook cases (skills.md section 10) without a dedicated PII service.
_EMAIL_RE = re.compile(r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+\b")
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_CREDIT_CARD_GROUPED_RE = re.compile(r"\b\d{4}[ -]\d{4}[ -]\d{4}[ -]\d{1,4}\b")
_CREDIT_CARD_CONTIGUOUS_RE = re.compile(r"\b\d{13,16}\b")
_PHONE_RE = re.compile(r"\b(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b")

_PATTERNS = {
    "email": _EMAIL_RE,
    "ssn": _SSN_RE,
    "credit_card": _CREDIT_CARD_GROUPED_RE,
    "phone": _PHONE_RE,
}


def detect_pii(text: str) -> list[str]:
    found = [label for label, pattern in _PATTERNS.items() if pattern.search(text)]
    if _CREDIT_CARD_CONTIGUOUS_RE.search(text) and "credit_card" not in found:
        found.append("credit_card")
    return found


def redact_pii(text: str) -> str:
    text = _EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = _SSN_RE.sub("[REDACTED_SSN]", text)
    text = _CREDIT_CARD_GROUPED_RE.sub("[REDACTED_CARD]", text)
    text = _CREDIT_CARD_CONTIGUOUS_RE.sub("[REDACTED_CARD]", text)
    text = _PHONE_RE.sub("[REDACTED_PHONE]", text)
    return text
