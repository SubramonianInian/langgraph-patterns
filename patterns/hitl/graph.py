"""Human-in-the-Loop pattern.

An agent proposes an action, then pauses via LangGraph's ``interrupt``. The
caller resumes the graph with an approval + optional feedback. Approved
actions execute; rejected ones route back to a revision node.

The checkpointer is mandatory — interrupts persist graph state between the
pause and the resume.
"""

from typing import TypedDict

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt
from pydantic import BaseModel, Field

from shared.llm import get_model


class Proposal(BaseModel):
    action: str = Field(description="The proposed action in one sentence.")
    rationale: str = Field(description="Why this action addresses the request.")


class State(TypedDict):
    request: str
    proposal: str
    rationale: str
    approved: bool
    human_feedback: str
    final: str


def propose(state: State) -> dict:
    model = get_model().with_structured_output(Proposal)
    prop = model.invoke(
        [HumanMessage(content=f"Propose a single concrete action for: {state['request']}")]
    )
    return {"proposal": prop.action, "rationale": prop.rationale}


def human_review(state: State) -> dict:
    """Pauses graph execution until the caller supplies a decision."""
    decision = interrupt(
        {
            "proposal": state["proposal"],
            "rationale": state["rationale"],
            "awaiting": "approval",
        }
    )
    return {
        "approved": bool(decision.get("approved", False)),
        "human_feedback": decision.get("feedback", ""),
    }


def execute(state: State) -> dict:
    return {"final": f"EXECUTED: {state['proposal']}"}


def revise(state: State) -> dict:
    model = get_model().with_structured_output(Proposal)
    prompt = (
        f"Original request: {state['request']}\n\n"
        f"Previous proposal (rejected): {state['proposal']}\n"
        f"Reviewer feedback: {state['human_feedback']}\n\n"
        "Propose a revised action that addresses the feedback."
    )
    prop = model.invoke([HumanMessage(content=prompt)])
    return {"proposal": prop.action, "rationale": prop.rationale}


def _after_review(state: State) -> str:
    return "execute" if state["approved"] else "revise"


def build_graph():
    graph = StateGraph(State)
    graph.add_node("propose", propose)
    graph.add_node("human_review", human_review)
    graph.add_node("revise", revise)
    graph.add_node("execute", execute)

    graph.add_edge(START, "propose")
    graph.add_edge("propose", "human_review")
    graph.add_conditional_edges(
        "human_review", _after_review, {"execute": "execute", "revise": "revise"}
    )
    graph.add_edge("revise", "human_review")
    graph.add_edge("execute", END)

    return graph.compile(checkpointer=InMemorySaver())
