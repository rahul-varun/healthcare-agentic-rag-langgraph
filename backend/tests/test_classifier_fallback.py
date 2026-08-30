from app.agents.classifier import fallback_classify
from app.prompts.classifier import parse_intent


def test_fallback_detects_calculation():
    assert fallback_classify("What was the revenue growth rate?") == "calculation"


def test_fallback_detects_relationship():
    assert fallback_classify("How is Company A connected to Company B?") == "relationship"


def test_fallback_detects_explanation():
    assert fallback_classify("Why did revenue decline?") == "explanation"


def test_fallback_defaults_to_factual():
    assert fallback_classify("What is Company A's 2025 revenue?") == "factual"


def test_parse_intent_extracts_known_label():
    assert parse_intent("  Factual  ") == "factual"


def test_parse_intent_returns_none_for_unknown_label():
    assert parse_intent("something else entirely") is None
