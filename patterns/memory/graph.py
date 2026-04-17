"""Memory pattern — short-term conversation + long-term facts.

Two memory tiers, kept deliberately distinct:
  * Short-term: conversation messages, ephemeral, lives in graph state
  * Long-term: durable facts about the user, lookup-indexed, lives outside state

The recall node pulls relevant long-term facts *into* the prompt for this turn.
The extract node decides if anything in the user's message is worth writing
back to long-term memory for future turns.
"""

from typing import TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from patterns.memory.store import STORE
from shared.llm import get_model
from shared.prompts import load as load_prompts

PROMPTS = load_prompts(__file__)


class FactExtraction(BaseModel):
    facts: list[str] = Field(
        description=(
            "Durable facts about the user worth remembering across sessions. "
            "Empty list if nothing qualifies. Skip transient chat."
        )
    )


class Message(TypedDict):
    role: str
    content: str


class State(TypedDict):
    user_id: str
    messages: list[Message]
    recalled: list[str]
    response: str


def recall(state: State) -> dict:
    query = state["messages"][-1]["content"]
    hits = STORE.read(state["user_id"], query)
    return {"recalled": hits}


def respond(state: State) -> dict:
    recalled = "\n".join(f"- {m}" for m in state["recalled"]) or "(no prior facts)"
    history = "\n".join(f"{m['role']}: {m['content']}" for m in state["messages"])
    prompt = PROMPTS["respond"].format(recalled=recalled, history=history)
    response = get_model().invoke([HumanMessage(content=prompt)])
    return {"response": response.content}


def extract(state: State) -> dict:
    last_user = state["messages"][-1]["content"]
    model = get_model().with_structured_output(FactExtraction)
    result = model.invoke(
        [HumanMessage(content=PROMPTS["extract"].format(message=last_user))]
    )
    for fact in result.facts:
        STORE.write(state["user_id"], fact)
    return {}


def build_graph():
    graph = StateGraph(State)
    graph.add_node("recall", recall)
    graph.add_node("respond", respond)
    graph.add_node("extract", extract)

    graph.add_edge(START, "recall")
    graph.add_edge("recall", "respond")
    graph.add_edge("respond", "extract")
    graph.add_edge("extract", END)

    return graph.compile()
