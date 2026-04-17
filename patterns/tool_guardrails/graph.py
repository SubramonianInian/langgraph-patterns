"""Tool Guardrails pattern.

A model proposes a tool call with structured arguments. A validator node
runs declarative checks (Pydantic + explicit business rules). If validation
fails, the model gets the errors and retries. Only validated calls reach
the executor — so tools don't need defensive parsing of untrusted input.

The demo tool is a read-only SQL query runner that refuses mutations and
bounds result size.
"""

import re
from typing import TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field, ValidationError

from shared.llm import get_model
from shared.prompts import load as load_prompts

PROMPTS = load_prompts(__file__)


class SqlQuery(BaseModel):
    sql: str = Field(description="A single SELECT statement, no semicolons, no comments.")
    reason: str = Field(description="One sentence: why this query answers the question.")


FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|truncate|alter|create|grant|revoke)\b", re.IGNORECASE
)
MAX_LIMIT = 100


class State(TypedDict):
    question: str
    proposed_sql: str
    proposed_reason: str
    validation_errors: list[str]
    attempts: int
    max_attempts: int
    result: str


def propose_tool_call(state: State) -> dict:
    feedback = ""
    if state.get("validation_errors"):
        feedback = PROMPTS["retry_feedback"].format(
            errors="\n".join(f"- {e}" for e in state["validation_errors"])
        )
    model = get_model().with_structured_output(SqlQuery)
    prompt = PROMPTS["propose"].format(question=state["question"], feedback=feedback)
    try:
        proposal = model.invoke([HumanMessage(content=prompt)])
    except ValidationError as e:
        return {
            "proposed_sql": "",
            "proposed_reason": "",
            "validation_errors": [f"Model output failed schema: {e}"],
            "attempts": state.get("attempts", 0) + 1,
        }
    return {
        "proposed_sql": proposal.sql,
        "proposed_reason": proposal.reason,
        "validation_errors": [],
        "attempts": state.get("attempts", 0) + 1,
    }


def validate(state: State) -> dict:
    sql = state["proposed_sql"].strip()
    errors: list[str] = []

    if not sql.lower().startswith("select"):
        errors.append("Query must begin with SELECT.")
    if ";" in sql:
        errors.append("Semicolons are not allowed (prevents query chaining).")
    if FORBIDDEN.search(sql):
        errors.append("Mutation keywords (INSERT/UPDATE/DELETE/DROP/etc.) are forbidden.")
    if "--" in sql or "/*" in sql:
        errors.append("SQL comments are not allowed.")

    # Enforce LIMIT <= MAX_LIMIT.
    limit_match = re.search(r"\blimit\s+(\d+)\b", sql, re.IGNORECASE)
    if limit_match:
        if int(limit_match.group(1)) > MAX_LIMIT:
            errors.append(f"LIMIT exceeds {MAX_LIMIT}.")
    else:
        errors.append(f"Query must include an explicit LIMIT (<= {MAX_LIMIT}).")

    return {"validation_errors": errors}


def execute_tool(state: State) -> dict:
    # In a real system this would hit the database. Demo returns a synthetic
    # success string so the graph flow is visible.
    return {
        "result": (
            f"[EXECUTED] {state['proposed_sql']}\n"
            f"Rationale: {state['proposed_reason']}\n"
            f"(returned: mock 3 rows)"
        )
    }


def give_up(state: State) -> dict:
    return {
        "result": (
            "Could not produce a valid query after "
            f"{state['attempts']} attempts. Last errors:\n"
            + "\n".join(f"- {e}" for e in state["validation_errors"])
        )
    }


def _after_validate(state: State) -> str:
    if not state["validation_errors"]:
        return "execute"
    if state["attempts"] >= state["max_attempts"]:
        return "give_up"
    return "retry"


def build_graph():
    graph = StateGraph(State)
    graph.add_node("propose", propose_tool_call)
    graph.add_node("validate", validate)
    graph.add_node("execute", execute_tool)
    graph.add_node("give_up", give_up)

    graph.add_edge(START, "propose")
    graph.add_edge("propose", "validate")
    graph.add_conditional_edges(
        "validate",
        _after_validate,
        {"execute": "execute", "retry": "propose", "give_up": "give_up"},
    )
    graph.add_edge("execute", END)
    graph.add_edge("give_up", END)

    return graph.compile()
