import math

import pytest

from app.evaluation.metrics import hit_rate, ndcg_at_k, precision_at_k, recall_at_k, reciprocal_rank


def test_hit_rate_true_when_any_relevant():
    assert hit_rate([False, True, False]) == 1.0


def test_hit_rate_zero_when_none_relevant():
    assert hit_rate([False, False]) == 0.0


def test_reciprocal_rank_first_position():
    assert reciprocal_rank([True, False, False]) == 1.0


def test_reciprocal_rank_third_position():
    assert reciprocal_rank([False, False, True]) == pytest.approx(1 / 3)


def test_reciprocal_rank_zero_when_not_found():
    assert reciprocal_rank([False, False]) == 0.0


def test_recall_at_k_full_recall():
    assert recall_at_k([True, True], total_relevant=2) == 1.0


def test_recall_at_k_partial():
    assert recall_at_k([True, False], total_relevant=2) == 0.5


def test_recall_at_k_zero_total_relevant():
    assert recall_at_k([False], total_relevant=0) == 0.0


def test_precision_at_k():
    assert precision_at_k([True, False, True, False]) == 0.5


def test_precision_at_k_empty():
    assert precision_at_k([]) == 0.0


def test_ndcg_perfect_when_relevant_first():
    assert ndcg_at_k([True, False, False], ideal_relevant_count=1) == 1.0


def test_ndcg_lower_when_relevant_later():
    score_first = ndcg_at_k([True, False], ideal_relevant_count=1)
    score_second = ndcg_at_k([False, True], ideal_relevant_count=1)
    assert score_second < score_first
    assert score_second == pytest.approx(1 / math.log2(3))


def test_ndcg_zero_when_no_relevant_found():
    assert ndcg_at_k([False, False], ideal_relevant_count=1) == 0.0
