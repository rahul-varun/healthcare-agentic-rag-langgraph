# Routing table from skills.md section 7 (Agentic Routing).
_INTENT_TO_TOOLS: dict[str, list[str]] = {
    "factual": ["retrieve"],
    "calculation": ["sql", "calculator"],
    "relationship": ["graph_search"],
    "explanation": ["retrieve", "web_search"],
    "complex_research": ["retrieve", "graph_search", "sql", "web_search"],
}


def plan_for_intent(intent: str) -> list[str]:
    return list(_INTENT_TO_TOOLS.get(intent, ["retrieve"]))
