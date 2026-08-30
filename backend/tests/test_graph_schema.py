from app.graph.schema import is_valid_triple
from app.models.triple import Triple


def _triple(**overrides) -> Triple:
    base = dict(
        subject="Company A",
        subject_type="Company",
        predicate="ACQUIRED",
        object="Company B",
        object_type="Company",
    )
    base.update(overrides)
    return Triple(**base)


def test_valid_triple_passes():
    assert is_valid_triple(_triple()) is True


def test_unknown_predicate_rejected():
    assert is_valid_triple(_triple(predicate="DESTROYED")) is False


def test_unknown_entity_type_rejected():
    assert is_valid_triple(_triple(subject_type="Vehicle")) is False
    assert is_valid_triple(_triple(object_type="Vehicle")) is False


def test_empty_subject_or_object_rejected():
    assert is_valid_triple(_triple(subject="")) is False
    assert is_valid_triple(_triple(object="")) is False
