import asyncio

from app.observability.tracing import traced


def test_traced_records_node_name_and_duration():
    @traced("my_node")
    async def node(state):
        return {"foo": "bar"}

    result = asyncio.run(node({}))
    assert result["foo"] == "bar"
    assert len(result["trace"]) == 1
    assert result["trace"][0]["node"] == "my_node"
    assert result["trace"][0]["duration_ms"] >= 0


def test_traced_does_not_mutate_original_result_dict():
    original = {"foo": "bar"}

    @traced("my_node")
    async def node(state):
        return original

    result = asyncio.run(node({}))
    assert "trace" not in original
    assert "trace" in result
