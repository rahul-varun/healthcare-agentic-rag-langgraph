import functools
import time
from typing import Awaitable, Callable

NodeFn = Callable[[dict], Awaitable[dict]]


def traced(name: str) -> Callable[[NodeFn], NodeFn]:
    """Wraps a LangGraph node to record its own timing into state['trace'], which
    accumulates via AgentState's operator.add reducer — matches the per-node
    trace format in skills.md section 15 (Guardrail 40ms, Classifier 110ms, ...)."""

    def decorator(fn: NodeFn) -> NodeFn:
        @functools.wraps(fn)
        async def wrapper(state: dict) -> dict:
            start = time.perf_counter()
            result = await fn(state)
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            result = dict(result)
            result["trace"] = [{"node": name, "duration_ms": duration_ms}]
            return result

        return wrapper

    return decorator
