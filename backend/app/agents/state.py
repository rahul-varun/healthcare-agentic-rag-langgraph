import operator
from typing import Annotated, TypedDict


class AgentState(TypedDict, total=False):
    query: str
    response_language: str
    rewritten_query: str
    intent: str
    plan: list[str]
    remaining_tools: list[str]
    top_k: int
    filters: dict | None

    evidence: Annotated[list[dict], operator.add]
    tool_calls: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]
    trace: Annotated[list[dict], operator.add]

    draft_answer: str
    verification: dict
    final_answer: str
    output_policy: str
    specialist_reports: dict[str, str]

    blocked: bool
    blocked_reason: str | None
