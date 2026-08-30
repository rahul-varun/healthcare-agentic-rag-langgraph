from app.graph.extraction import parse_triples


def test_parses_clean_json_array():
    raw = """[
        {"subject": "Company A", "subject_type": "Company", "predicate": "ACQUIRED",
         "object": "Company B", "object_type": "Company"}
    ]"""
    triples = parse_triples(raw)
    assert len(triples) == 1
    assert triples[0].subject == "Company A"
    assert triples[0].predicate == "ACQUIRED"


def test_strips_markdown_code_fences():
    raw = '```json\n[{"subject": "A", "subject_type": "Company", "predicate": "acquired", ' \
          '"object": "B", "object_type": "Company"}]\n```'
    triples = parse_triples(raw)
    assert len(triples) == 1
    assert triples[0].predicate == "ACQUIRED"  # normalized to uppercase


def test_invalid_json_returns_empty_list():
    assert parse_triples("not json at all") == []


def test_non_list_json_returns_empty_list():
    assert parse_triples('{"subject": "A"}') == []


def test_unknown_predicate_is_filtered_out():
    raw = '[{"subject": "A", "subject_type": "Company", "predicate": "DESTROYED", ' \
          '"object": "B", "object_type": "Company"}]'
    assert parse_triples(raw) == []


def test_missing_keys_are_skipped():
    raw = '[{"subject": "A", "predicate": "ACQUIRED"}]'
    assert parse_triples(raw) == []


def test_empty_array_returns_empty_list():
    assert parse_triples("[]") == []
