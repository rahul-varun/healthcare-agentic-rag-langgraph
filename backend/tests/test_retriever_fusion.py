from app.retrieval.retriever import _matches_filters, _reciprocal_rank_fusion


def test_rrf_favors_docs_ranked_high_in_both_lists():
    dense = ["a", "b", "c"]
    bm25 = ["b", "a", "d"]
    scores = _reciprocal_rank_fusion(dense, bm25)
    assert scores["a"] > scores["c"]
    assert scores["b"] > scores["c"]
    assert "d" in scores


def test_rrf_with_empty_list_is_a_noop():
    scores = _reciprocal_rank_fusion(["a", "b"], [])
    assert scores["a"] > scores["b"]


def test_matches_filters_none_accepts_everything():
    assert _matches_filters({"company": "Acme"}, None) is True


def test_matches_filters_requires_all_keys_to_match():
    metadata = {"company": "Acme", "year": 2026}
    assert _matches_filters(metadata, {"company": "Acme"}) is True
    assert _matches_filters(metadata, {"company": "Acme", "year": 2025}) is False
    assert _matches_filters(metadata, {"company": "Other"}) is False
