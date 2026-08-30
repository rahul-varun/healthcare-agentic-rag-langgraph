from functools import lru_cache

from langgraph.graph import END, StateGraph

from app.agents.classifier import classify_intent
from app.agents.evidence_check import verify_claims
from app.agents.llm_client import generate
from app.agents.planner import plan_for_intent
from app.agents.rewriter import rewrite_query
from app.agents.sql_generation import generate_sql
from app.agents.specialists import run_specialist
from app.agents.state import AgentState
from app.config.settings import get_settings
from app.guardrails.input_guardrail import check_input
from app.guardrails.output_guardrail import apply_output_guardrail
from app.observability.tracing import traced
from app.prompts.rag import SYSTEM_PROMPT, build_prompt
from app.tools.calculator_tool import CalculatorError, evaluate, extract_expression
from app.tools.document_tool import search_documents
from app.tools.graph_tool import search_graph
from app.tools.sql_tool import SQLExecutionError, SQLGuardError, query_sql
from app.tools.web_tool import WebSearchError, search_web

_TOOL_NODE_NAMES = ("retrieve", "graph_search", "sql", "web_search", "calculator")


@traced("guardrail")
async def guardrail_node(state: AgentState) -> dict:
    settings = get_settings()
    blocked, reason = check_input(state["query"], max_chars=settings.max_input_chars)
    update: dict = {"blocked": blocked, "blocked_reason": reason}
    if blocked:
        update["final_answer"] = f"Request blocked by input guardrails: {reason}"
    return update


@traced("classifier")
async def classifier_node(state: AgentState) -> dict:
    intent = await classify_intent(state["query"], get_settings())
    return {"intent": intent}


@traced("rewriter")
async def rewriter_node(state: AgentState) -> dict:
    rewritten = await rewrite_query(state["query"], get_settings())
    return {"rewritten_query": rewritten}


@traced("planner")
async def planner_node(state: AgentState) -> dict:
    plan = plan_for_intent(state["intent"])
    return {"plan": plan, "remaining_tools": plan}


def _effective_query(state: AgentState) -> str:
    return state.get("rewritten_query") or state["query"]


def _pop_remaining(state: AgentState) -> list[str]:
    return state.get("remaining_tools", [])[1:]


@traced("retrieve")
async def retrieve_node(state: AgentState) -> dict:
    evidence = search_documents(_effective_query(state), top_k=state.get("top_k", 5), filters=state.get("filters"))
    return {"evidence": evidence, "remaining_tools": _pop_remaining(state), "tool_calls": ["retrieve"]}


@traced("graph_search")
async def graph_search_node(state: AgentState) -> dict:
    evidence = search_graph(_effective_query(state))
    return {"evidence": evidence, "remaining_tools": _pop_remaining(state), "tool_calls": ["graph_search"]}


@traced("sql")
async def sql_node(state: AgentState) -> dict:
    settings = get_settings()
    question = _effective_query(state)
    sql_query = await generate_sql(question, settings)
    if not sql_query:
        return {
            "evidence": [],
            "remaining_tools": _pop_remaining(state),
            "tool_calls": ["sql"],
            "errors": ["SQL generation produced no query for this question"],
        }
    try:
        rows = query_sql(sql_query, max_rows=settings.sql_max_rows, timeout_seconds=settings.sql_timeout_seconds)
    except (SQLGuardError, SQLExecutionError) as exc:
        return {"evidence": [], "remaining_tools": _pop_remaining(state), "tool_calls": ["sql"], "errors": [str(exc)]}
    evidence = [{"text": str(row), "metadata": row, "source": "sql"} for row in rows]
    return {"evidence": evidence, "remaining_tools": _pop_remaining(state), "tool_calls": ["sql"]}


@traced("web_search")
async def web_search_node(state: AgentState) -> dict:
    settings = get_settings()
    try:
        results = await search_web(_effective_query(state), settings)
    except WebSearchError as exc:
        return {
            "evidence": [],
            "remaining_tools": _pop_remaining(state),
            "tool_calls": ["web_search"],
            "errors": [str(exc)],
        }
    evidence = [
        {"text": f"{r['title']}: {r['content']}", "metadata": {"url": r["url"], "title": r["title"]}, "source": "web_search"}
        for r in results
    ]
    return {"evidence": evidence, "remaining_tools": _pop_remaining(state), "tool_calls": ["web_search"]}


@traced("calculator")
async def calculator_node(state: AgentState) -> dict:
    expression = extract_expression(_effective_query(state))
    if expression is None:
        return {
            "evidence": [],
            "remaining_tools": _pop_remaining(state),
            "tool_calls": ["calculator"],
            "errors": ["No arithmetic expression found for the calculator tool"],
        }
    try:
        result = evaluate(expression)
    except CalculatorError as exc:
        return {
            "evidence": [],
            "remaining_tools": _pop_remaining(state),
            "tool_calls": ["calculator"],
            "errors": [f"calculator failed: {exc}"],
        }
    evidence = [
        {
            "text": f"Calculated: {expression} = {result}",
            "metadata": {"expression": expression, "result": result},
            "source": "calculator",
        }
    ]
    return {"evidence": evidence, "remaining_tools": _pop_remaining(state), "tool_calls": ["calculator"]}


async def _specialist_node(state: AgentState, name: str) -> dict:
    report = await run_specialist(name, _effective_query(state), state.get("evidence", []), get_settings())
    reports = dict(state.get("specialist_reports", {}))
    reports[name] = report
    return {"specialist_reports": reports, "tool_calls": [f"agent:{name}"]}


@traced("clinical_info_agent")
async def clinical_info_agent_node(state: AgentState) -> dict:
    return await _specialist_node(state, "clinical_info")


@traced("medication_safety_agent")
async def medication_safety_agent_node(state: AgentState) -> dict:
    return await _specialist_node(state, "medication_safety")


@traced("web_evidence_agent")
async def web_evidence_agent_node(state: AgentState) -> dict:
    return await _specialist_node(state, "web_evidence")


def route_next_tool(state: AgentState) -> str:
    remaining = state.get("remaining_tools") or []
    if not remaining:
        return "clinical_info_agent"
    # Defense in depth (skills.md section 17: "Never allow infinite agent
    # loops"). The planner's lists are always short and finite today, so this
    # shouldn't trigger — it's a hard ceiling, not the primary control.
    if len(state.get("tool_calls", [])) >= get_settings().max_agent_iterations:
        return "generate"
    return remaining[0]


@traced("generate")
async def generate_node(state: AgentState) -> dict:
    evidence = state.get("evidence", [])
    if not evidence:
        return {"draft_answer": "No evidence was found for this query using the available tools."}
    prompt = build_prompt(
        _effective_query(state),
        evidence,
        state.get("specialist_reports", {}),
        state.get("response_language", "english"),
    )
    language = state.get("response_language", "english")
    language_instruction = {
        "english": "Answer in clear English.",
        "hindi": "Answer in natural Hindi using Devanagari script.",
        "hinglish": "Answer in natural Hinglish using Roman script (Hindi words written in English letters).",
        "tamil": "Answer in natural Tamil using Tamil script.",
    }.get(language, "Answer in clear English.")
    draft = await generate(
        prompt,
        get_settings(),
        system=f"{SYSTEM_PROMPT}\n\nResponse language requirement: {language_instruction}",
    )
    return {"draft_answer": draft}


@traced("evidence_check")
async def evidence_check_node(state: AgentState) -> dict:
    verification = await verify_claims(state["draft_answer"], state.get("evidence", []), get_settings())
    return {"verification": verification}


@traced("output_guardrail")
async def output_guardrail_node(state: AgentState) -> dict:
    final_answer, output_policy = apply_output_guardrail(state["draft_answer"], state.get("verification"))
    return {"final_answer": final_answer, "output_policy": output_policy}


def build_agent_graph():
    graph = StateGraph(AgentState)
    graph.add_node("guardrail", guardrail_node)
    graph.add_node("classifier", classifier_node)
    graph.add_node("rewriter", rewriter_node)
    graph.add_node("planner", planner_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("graph_search", graph_search_node)
    graph.add_node("sql", sql_node)
    graph.add_node("web_search", web_search_node)
    graph.add_node("calculator", calculator_node)
    graph.add_node("clinical_info_agent", clinical_info_agent_node)
    graph.add_node("medication_safety_agent", medication_safety_agent_node)
    graph.add_node("web_evidence_agent", web_evidence_agent_node)
    graph.add_node("generate", generate_node)
    graph.add_node("evidence_check", evidence_check_node)
    graph.add_node("output_guardrail", output_guardrail_node)

    graph.set_entry_point("guardrail")
    graph.add_conditional_edges(
        "guardrail",
        lambda state: "blocked" if state.get("blocked") else "continue",
        {"blocked": END, "continue": "classifier"},
    )
    graph.add_edge("classifier", "rewriter")
    graph.add_edge("rewriter", "planner")

    dispatch_map = {name: name for name in _TOOL_NODE_NAMES} | {
        "clinical_info_agent": "clinical_info_agent",
        "generate": "generate",
    }
    graph.add_conditional_edges("planner", route_next_tool, dispatch_map)
    for tool_name in _TOOL_NODE_NAMES:
        graph.add_conditional_edges(tool_name, route_next_tool, dispatch_map)

    graph.add_edge("clinical_info_agent", "medication_safety_agent")
    graph.add_edge("medication_safety_agent", "web_evidence_agent")
    graph.add_edge("web_evidence_agent", "generate")
    graph.add_edge("generate", "evidence_check")
    graph.add_edge("evidence_check", "output_guardrail")
    graph.add_edge("output_guardrail", END)
    return graph.compile()


@lru_cache
def get_agent_graph():
    return build_agent_graph()


async def run_agent(
    query: str,
    top_k: int = 5,
    filters: dict | None = None,
    response_language: str = "english",
) -> AgentState:
    initial_state: AgentState = {
        "query": query,
        "response_language": response_language if response_language in {"english", "hindi", "hinglish", "tamil"} else "english",
        "top_k": top_k,
        "filters": filters,
        "evidence": [],
        "tool_calls": [],
        "errors": [],
        "trace": [],
        "specialist_reports": {},
    }
    return await get_agent_graph().ainvoke(initial_state)
