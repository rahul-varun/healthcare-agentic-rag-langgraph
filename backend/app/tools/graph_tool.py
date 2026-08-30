import re

from neo4j.exceptions import GqlError

from app.graph.neo4j_client import get_neo4j_client

# Proper-noun heuristic, not real entity linking — good enough to seed graph
# lookups for this phase's scaffold. A real system would match against the set
# of entity names actually stored in the graph (or run NER) instead of guessing
# from capitalization.
_ENTITY_RE = re.compile(r"\b[A-Z][a-zA-Z0-9&]*(?:\s+[A-Z][a-zA-Z0-9&]*)*\b")


def extract_candidate_entities(text: str) -> list[str]:
    candidates = {match.group(0) for match in _ENTITY_RE.finditer(text)}
    return [c for c in candidates if len(c) > 2]


def search_graph(query: str, max_hops: int = 2) -> list[dict]:
    client = get_neo4j_client()
    evidence = []
    for entity in extract_candidate_entities(query):
        try:
            hits = client.related(entity, max_hops=max_hops)
        except GqlError:
            continue
        for hit in hits:
            relationships = ", ".join(hit.get("relationships", []))
            evidence.append(
                {
                    "text": f"{hit.get('source')} -[{relationships}]-> {hit.get('target')}",
                    "metadata": hit,
                    "source": "knowledge_graph",
                }
            )
    return evidence
