import json
import re

_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def parse_json_object(raw: str) -> dict | list | None:
    """Best-effort JSON parse of an LLM response, tolerating markdown code fences.
    Returns None on anything that doesn't parse — callers must not trust LLM
    output blindly, so a parse failure is always treated as "no data" rather
    than raising."""
    text = _CODE_FENCE_RE.sub("", raw.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
