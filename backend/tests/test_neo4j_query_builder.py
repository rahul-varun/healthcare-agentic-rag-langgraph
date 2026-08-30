import pytest

from app.graph.neo4j_client import GraphError, build_path_query, build_related_query, build_upsert_query


def test_build_upsert_query_interpolates_valid_relation():
    query = build_upsert_query("ACQUIRED")
    assert "MERGE (s)-[r:ACQUIRED]->(o)" in query
    assert "$subject" in query and "$object" in query


def test_build_upsert_query_rejects_unknown_relation():
    with pytest.raises(GraphError):
        build_upsert_query("DROP DATABASE neo4j")


def test_build_related_query_clamps_hops_to_range():
    assert "*1..5" in build_related_query(max_hops=99)
    assert "*1..1" in build_related_query(max_hops=0)
    assert "*1..2" in build_related_query(max_hops=2)


def test_build_path_query_clamps_hops_to_range():
    assert "*..5" in build_path_query(max_hops=999)
    assert "*..1" in build_path_query(max_hops=-3)
