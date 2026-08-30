from app.observability.metrics import MetricsRegistry


def test_records_requests_and_errors():
    registry = MetricsRegistry()
    registry.record_request()
    registry.record_request()
    registry.record_error()
    snapshot = registry.snapshot()
    assert snapshot["request_count"] == 2
    assert snapshot["error_count"] == 1


def test_records_token_usage():
    registry = MetricsRegistry()
    registry.record_llm_usage(100, 50)
    registry.record_llm_usage(200, 75)
    snapshot = registry.snapshot()
    assert snapshot["total_input_tokens"] == 300
    assert snapshot["total_output_tokens"] == 125


def test_estimates_cost_from_token_usage():
    registry = MetricsRegistry()
    registry.record_llm_usage(1000, 1000)
    cost = registry.estimate_cost_usd(cost_per_1k_input=1.0, cost_per_1k_output=2.0)
    assert cost == 3.0


def test_records_tool_call_counts():
    registry = MetricsRegistry()
    registry.record_tool_calls(["retrieve", "retrieve", "graph_search"])
    snapshot = registry.snapshot()
    assert snapshot["tool_call_counts"] == {"retrieve": 2, "graph_search": 1}
