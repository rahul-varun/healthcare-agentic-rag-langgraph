import re

_CLINICAL_ACTION_RE = re.compile(
    r"\b(?:take|give|start|stop|increase|decrease|prescribe|inject|dose|dosage|mg/kg|"
    r"diagnos(?:e|is)|antibiotic|iv fluids?|intravenous|treatment plan)\b",
    re.IGNORECASE,
)
_SAFETY_LANGUAGE_RE = re.compile(
    r"\b(?:doctor|clinician|healthcare professional|urgent care|emergency|call emergency|"
    r"seek medical|not a diagnosis|do not self|confirm with)\b",
    re.IGNORECASE,
)


def needs_medical_safety_note(answer: str) -> bool:
    """Flag clinical-action language that needs an explicit safety boundary."""
    return bool(_CLINICAL_ACTION_RE.search(answer)) and not bool(_SAFETY_LANGUAGE_RE.search(answer))
