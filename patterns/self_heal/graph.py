"""Self-Heal pattern.

Graceful degradation for tool or model failures. A tiered fallback chain:

    primary tool → secondary tool → cached answer → honest apology

Each tier is a distinct node so failures are visible and the chosen path is
auditable. Nothing silently retries; nothing silently lies about what
happened — state records the degradation level that served the final answer.
"""

import random
from typing import TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

from shared.llm import get_model


class ToolError(RuntimeError):
    pass


class State(TypedDict):
    query: str
    attempts: list[str]        # what we tried, in order
    degradation_level: int     # 0=primary, 1=secondary, 2=cache, 3=apology
    response: str


# ---- simulated external dependencies ----------------------------------------


def _primary_search(query: str) -> str:
    """Pretend this is a premium search API that sometimes fails."""
    if random.random() < 0.9:
        raise ToolError("primary search: 503 Service Unavailable")
    return f"primary-result for: {query}"


def _secondary_search(query: str) -> str:
    """Pretend this is a cheaper, less accurate search API."""
    if random.random() < 0.6:
        raise ToolError("secondary search: timeout")
    return f"secondary-result for: {query}"


_CACHE: dict[str, str] = {
    "what is RAG?": "RAG retrieves documents to ground an LLM's answer.",
}


# ---- graph nodes ------------------------------------------------------------


def primary(state: State) -> dict:
    attempts = state.get("attempts", []) + ["primary"]
    try:
        evidence = _primary_search(state["query"])
    except ToolError as e:
        return {"attempts": attempts + [f"primary-failed: {e}"]}
    response = get_model().invoke(
        [HumanMessage(content=f"Answer using only:\n{evidence}\n\nQuestion: {state['query']}")]
    )
    return {
        "attempts": attempts,
        "degradation_level": 0,
        "response": response.content,
    }


def secondary(state: State) -> dict:
    attempts = state["attempts"] + ["secondary"]
    try:
        evidence = _secondary_search(state["query"])
    except ToolError as e:
        return {"attempts": attempts + [f"secondary-failed: {e}"]}
    response = get_model().invoke(
        [HumanMessage(content=f"Answer using only:\n{evidence}\n\nQuestion: {state['query']}")]
    )
    return {
        "attempts": attempts,
        "degradation_level": 1,
        "response": response.content + "\n\n(served from secondary source — may be less fresh)",
    }


def cache(state: State) -> dict:
    attempts = state["attempts"] + ["cache"]
    cached = _CACHE.get(state["query"].lower().strip())
    if cached is None:
        return {"attempts": attempts + ["cache-miss"]}
    return {
        "attempts": attempts,
        "degradation_level": 2,
        "response": cached + "\n\n(served from cache — may be stale)",
    }


def apology(state: State) -> dict:
    return {
        "attempts": state["attempts"] + ["apology"],
        "degradation_level": 3,
        "response": (
            "I couldn't answer reliably right now — my primary and backup sources "
            "both failed, and nothing relevant is cached. Please try again shortly."
        ),
    }


def _responded(state: State) -> bool:
    return bool(state.get("response"))


def _after_primary(state: State) -> str:
    return "done" if _responded(state) else "fallback"


def _after_secondary(state: State) -> str:
    return "done" if _responded(state) else "fallback"


def _after_cache(state: State) -> str:
    return "done" if _responded(state) else "fallback"


def build_graph():
    graph = StateGraph(State)
    graph.add_node("primary", primary)
    graph.add_node("secondary", secondary)
    graph.add_node("cache", cache)
    graph.add_node("apology", apology)

    graph.add_edge(START, "primary")
    graph.add_conditional_edges(
        "primary", _after_primary, {"done": END, "fallback": "secondary"}
    )
    graph.add_conditional_edges(
        "secondary", _after_secondary, {"done": END, "fallback": "cache"}
    )
    graph.add_conditional_edges(
        "cache", _after_cache, {"done": END, "fallback": "apology"}
    )
    graph.add_edge("apology", END)

    return graph.compile()
