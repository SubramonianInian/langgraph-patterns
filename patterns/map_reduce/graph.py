"""Map-Reduce (Fan-out / Fan-in) pattern.

The dispatcher splits a list of inputs into N parallel worker invocations
using LangGraph's ``Send`` API. Worker outputs are concatenated via a
reducer on the shared state, then a synthesizer combines them.

This is the right structure any time you have an **embarrassingly parallel**
LLM workload — per-document summarization, per-item classification,
per-file code review.
"""

import operator
from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage
from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph

from shared.llm import get_model
from shared.prompts import load as load_prompts

PROMPTS = load_prompts(__file__)


class WorkerInput(TypedDict):
    item: str
    theme: str


class State(TypedDict):
    theme: str
    items: list[str]
    findings: Annotated[list[str], operator.add]
    synthesis: str


def dispatcher(state: State) -> list[Send]:
    """Fan out: one Send per item. LangGraph invokes `worker` in parallel for each."""
    return [Send("worker", {"item": item, "theme": state["theme"]}) for item in state["items"]]


def worker(inp: WorkerInput) -> dict:
    prompt = PROMPTS["worker"].format(theme=inp["theme"], item=inp["item"])
    response = get_model().invoke([HumanMessage(content=prompt)])
    return {"findings": [response.content]}


def synthesizer(state: State) -> dict:
    joined = "\n\n".join(f"- {f}" for f in state["findings"])
    prompt = PROMPTS["synthesizer"].format(theme=state["theme"], findings=joined)
    response = get_model().invoke([HumanMessage(content=prompt)])
    return {"synthesis": response.content}


def build_graph():
    graph = StateGraph(State)
    graph.add_node("worker", worker)
    graph.add_node("synthesizer", synthesizer)

    graph.add_conditional_edges(START, dispatcher, ["worker"])
    graph.add_edge("worker", "synthesizer")
    graph.add_edge("synthesizer", END)

    return graph.compile()
