"""Plan → Execute pattern.

A planner node produces an ordered list of steps. An executor runs them one
at a time. The plan is visible in state throughout execution — making the
agent's reasoning auditable and the execution pausable, replayable, and
amenable to mid-run replanning if needed.
"""

from typing import TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from shared.llm import get_model
from shared.prompts import load as load_prompts

PROMPTS = load_prompts(__file__)


class Plan(BaseModel):
    steps: list[str] = Field(
        description="Ordered list of concrete steps. 3-6 steps. Each step is imperative."
    )


class State(TypedDict):
    objective: str
    plan: list[str]
    current_step: int
    step_outputs: list[str]
    final: str


def planner(state: State) -> dict:
    model = get_model().with_structured_output(Plan)
    plan = model.invoke(
        [HumanMessage(content=PROMPTS["planner"].format(objective=state["objective"]))]
    )
    return {"plan": plan.steps, "current_step": 0, "step_outputs": []}


def executor(state: State) -> dict:
    step = state["plan"][state["current_step"]]
    prior = "\n".join(
        f"Step {i + 1}: {s}\n→ {o}"
        for i, (s, o) in enumerate(zip(state["plan"], state["step_outputs"]))
    )
    prompt = PROMPTS["executor"].format(
        objective=state["objective"], prior=prior or "(none)", step=step
    )
    response = get_model().invoke([HumanMessage(content=prompt)])
    return {
        "step_outputs": state["step_outputs"] + [response.content],
        "current_step": state["current_step"] + 1,
    }


def synthesize(state: State) -> dict:
    transcript = "\n\n".join(
        f"Step {i + 1}: {s}\n{o}"
        for i, (s, o) in enumerate(zip(state["plan"], state["step_outputs"]))
    )
    prompt = PROMPTS["synthesize"].format(
        objective=state["objective"], transcript=transcript
    )
    response = get_model().invoke([HumanMessage(content=prompt)])
    return {"final": response.content}


def _more_steps(state: State) -> str:
    return "continue" if state["current_step"] < len(state["plan"]) else "done"


def build_graph():
    graph = StateGraph(State)
    graph.add_node("planner", planner)
    graph.add_node("executor", executor)
    graph.add_node("synthesize", synthesize)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "executor")
    graph.add_conditional_edges(
        "executor", _more_steps, {"continue": "executor", "done": "synthesize"}
    )
    graph.add_edge("synthesize", END)

    return graph.compile()
