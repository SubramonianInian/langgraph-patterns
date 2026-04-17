"""Router / Supervisor pattern.

A supervisor node classifies the incoming question and dispatches it to one
of several specialist nodes. Each specialist is a leaf — but swap any of
them for a subgraph and you have a multi-agent system.
"""

from typing import Literal, TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from shared.llm import get_model
from shared.prompts import load as load_prompts

PROMPTS = load_prompts(__file__)

Specialist = Literal["code_review", "debugging", "design"]


class RouteDecision(BaseModel):
    specialist: Specialist = Field(description="Which specialist should handle the question.")
    reason: str = Field(description="One-sentence justification for the choice.")


class State(TypedDict):
    question: str
    route: Specialist | None
    route_reason: str | None
    answer: str | None


def supervisor(state: State) -> dict:
    model = get_model().with_structured_output(RouteDecision)
    decision = model.invoke(
        [HumanMessage(content=PROMPTS["supervisor"].format(question=state["question"]))]
    )
    return {"route": decision.specialist, "route_reason": decision.reason}


def _specialist(role: Specialist, state: State) -> dict:
    prompt = PROMPTS["specialist"].format(
        persona=PROMPTS["personas"][role], question=state["question"]
    )
    response = get_model().invoke([HumanMessage(content=prompt)])
    return {"answer": response.content}


def code_review_specialist(state: State) -> dict:
    return _specialist("code_review", state)


def debugging_specialist(state: State) -> dict:
    return _specialist("debugging", state)


def design_specialist(state: State) -> dict:
    return _specialist("design", state)


def _route(state: State) -> str:
    assert state["route"] is not None, "Supervisor must set a route before dispatch."
    return state["route"]


def build_graph():
    graph = StateGraph(State)
    graph.add_node("supervisor", supervisor)
    graph.add_node("code_review", code_review_specialist)
    graph.add_node("debugging", debugging_specialist)
    graph.add_node("design", design_specialist)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        _route,
        {"code_review": "code_review", "debugging": "debugging", "design": "design"},
    )
    graph.add_edge("code_review", END)
    graph.add_edge("debugging", END)
    graph.add_edge("design", END)

    return graph.compile()
