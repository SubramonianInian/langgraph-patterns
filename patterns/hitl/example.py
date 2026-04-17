"""Runnable demo of the Human-in-the-Loop pattern.

Simulates two review cycles: first a rejection with feedback, then an approval.

Usage:
    python -m patterns.hitl.example
"""

from langgraph.types import Command

from patterns.hitl.graph import build_graph


def _show_pending(graph, config) -> None:
    """Print whatever the graph is waiting on the caller to provide."""
    state = graph.get_state(config)
    for task in state.tasks:
        for interrupt in task.interrupts:
            payload = interrupt.value
            print(f"\n⏸  Graph paused — awaiting human review")
            print(f"   Proposal:  {payload.get('proposal')}")
            print(f"   Rationale: {payload.get('rationale')}")


def main() -> None:
    graph = build_graph()
    config = {"configurable": {"thread_id": "hitl-demo-1"}}

    initial = {
        "request": "Draft a message to the team announcing the API rate-limit change.",
        "proposal": "",
        "rationale": "",
        "approved": False,
        "human_feedback": "",
        "final": "",
    }

    print("▶  Starting graph...")
    graph.invoke(initial, config)
    _show_pending(graph, config)

    print("\n👤 Human rejects with feedback: 'Tone is too corporate, make it friendlier.'")
    graph.invoke(
        Command(
            resume={"approved": False, "feedback": "Tone is too corporate, make it friendlier."}
        ),
        config,
    )
    _show_pending(graph, config)

    print("\n👤 Human approves the revised proposal.")
    graph.invoke(Command(resume={"approved": True}), config)

    final = graph.get_state(config).values
    print(f"\n✅ Final: {final['final']}")


if __name__ == "__main__":
    main()
