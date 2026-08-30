import threading
from collections import Counter
from functools import lru_cache


class MetricsRegistry:
    """In-process metrics. Fine for a single-process dev/demo deployment; a real
    production deployment (Phase 9+) would export these to Prometheus/Langfuse
    instead of holding them in memory."""

    def __init__(self):
        # RLock, not Lock: snapshot() calls estimate_cost_usd() while already
        # holding the lock — a plain Lock would deadlock on that re-acquisition.
        self._lock = threading.RLock()
        self.request_count = 0
        self.error_count = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.tool_call_counts: Counter = Counter()

    def record_request(self) -> None:
        with self._lock:
            self.request_count += 1

    def record_error(self) -> None:
        with self._lock:
            self.error_count += 1

    def record_llm_usage(self, input_tokens: int, output_tokens: int) -> None:
        with self._lock:
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens

    def record_tool_calls(self, tool_calls: list[str]) -> None:
        with self._lock:
            self.tool_call_counts.update(tool_calls)

    def estimate_cost_usd(self, cost_per_1k_input: float, cost_per_1k_output: float) -> float:
        with self._lock:
            return (self.total_input_tokens / 1000) * cost_per_1k_input + (
                self.total_output_tokens / 1000
            ) * cost_per_1k_output

    def snapshot(self, cost_per_1k_input: float = 0.0, cost_per_1k_output: float = 0.0) -> dict:
        with self._lock:
            return {
                "request_count": self.request_count,
                "error_count": self.error_count,
                "total_input_tokens": self.total_input_tokens,
                "total_output_tokens": self.total_output_tokens,
                "tool_call_counts": dict(self.tool_call_counts),
                "estimated_cost_usd": self.estimate_cost_usd(cost_per_1k_input, cost_per_1k_output),
            }


@lru_cache
def get_metrics_registry() -> MetricsRegistry:
    return MetricsRegistry()
