from app.models.triple import Triple

# Entity/relationship vocabulary from skills.md section 4. Kept as a closed set —
# both for a coherent graph (no ad hoc relation sprawl) and because relationship
# types get interpolated directly into Cypher (Cypher can't parameterize them),
# so this allowlist doubles as the injection guard.
ALLOWED_ENTITY_TYPES = {
    "HealthPlan", "Insurer", "Member", "Benefit", "Treatment", "Medicine",
    "Hospital", "Doctor", "Condition", "Document", "Location", "Limit", "Period",
}

ALLOWED_RELATIONS = {
    "COVERS",
    "EXCLUDES",
    "REQUIRES_DOCUMENT",
    "TREATED_AT",
    "PRESCRIBED_FOR",
    "ELIGIBLE_FOR",
    "HAS_LIMIT",
    "HAS_WAITING_PERIOD",
    "LOCATED_IN",
    "FOR_PERIOD",
}


def is_valid_triple(triple: Triple) -> bool:
    if not triple.subject or not triple.object:
        return False
    if triple.predicate not in ALLOWED_RELATIONS:
        return False
    if triple.subject_type not in ALLOWED_ENTITY_TYPES:
        return False
    if triple.object_type not in ALLOWED_ENTITY_TYPES:
        return False
    return True
