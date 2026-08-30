from app.agents.planner import plan_for_intent


def test_factual_routes_to_retrieve():
    assert plan_for_intent("factual") == ["retrieve"]


def test_relationship_routes_to_graph_search():
    assert plan_for_intent("relationship") == ["graph_search"]


def test_complex_research_routes_to_all_tools():
    plan = plan_for_intent("complex_research")
    assert set(plan) == {"retrieve", "graph_search", "sql", "web_search"}


def test_unknown_intent_falls_back_to_retrieve():
    assert plan_for_intent("nonsense") == ["retrieve"]
