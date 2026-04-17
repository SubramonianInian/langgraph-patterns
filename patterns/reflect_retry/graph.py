"""Reflect & Retry pattern.

A writer produces a draft. A critic evaluates it against user-supplied criteria.
If the critic rejects the draft, the writer rewrites with feedback — capped by
`max_attempts` so the loop always terminates.
"""

from typing import TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from shared.llm import get_model
from shared.prompts import load as load_prompts

PROMPTS = load_prompts(__file__)


class Critique(BaseModel):
    passes: bool = Field(description="True if the draft satisfies ALL criteria.")
    feedback: str = Field(
        description="Specific, actionable improvements. Empty when passes is True."
    )


class State(TypedDict):
    topic: str
    criteria: str
    draft: str
    feedback: str
    attempts: int
    max_attempts: int
    passed: bool


def writer(state: State) -> dict:
    model = get_model()
    if state.get("feedback"):
        prompt = PROMPTS["rewrite"].format(
            topic=state["topic"],
            criteria=state["criteria"],
            draft=state["draft"],
            feedback=state["feedback"],
        )
    else:
        prompt = PROMPTS["writer"].format(topic=state["topic"], criteria=state["criteria"])
    response = model.invoke([HumanMessage(content=prompt)])
    return {"draft": response.content, "attempts": state.get("attempts", 0) + 1}


def critic(state: State) -> dict:
    model = get_model().with_structured_output(Critique)
    prompt = PROMPTS["critic"].format(criteria=state["criteria"], draft=state["draft"])
    critique = model.invoke([HumanMessage(content=prompt)])
    return {
        "passed": critique.passes,
        "feedback": "" if critique.passes else critique.feedback,
    }


def _next(state: State) -> str:
    if state["passed"]:
        return "end"
    if state["attempts"] >= state["max_attempts"]:
        return "end"
    return "retry"


def build_graph():
    graph = StateGraph(State)
    graph.add_node("writer", writer)
    graph.add_node("critic", critic)

    graph.add_edge(START, "writer")
    graph.add_edge("writer", "critic")
    graph.add_conditional_edges("critic", _next, {"retry": "writer", "end": END})

    return graph.compile()
