"""Runnable demo of the Human-in-the-Loop pattern.

Simulates two review cycles: first a rejection with feedback, then an approval.

Usage:
    python -m patterns.hitl.example
"""

from langgraph.types import Command

from patterns.hitl.graph import build_graph


def _print_interrupt(event: dict) -> None:
    for v in event.values():
        if isinstance(v, list):
            for item in v:
                if hasattr(item, "value"):
                    print(f"\n⏸  Graph paused — awaiting human review")
                    print(f"   Proposal:  {item.value.get('proposal')}")
                    print(f"   Rationale: {item.value.get('rationale')}")


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
    for event in graph.stream(initial, config):
        _print_interrupt(event)

    print("\n👤 Human rejects with feedback: 'Tone is too corporate, make it friendlier.'")
    for event in graph.stream(
        Command(resume={"approved": False, "feedback": "Tone is too corporate, make it friendlier."}),
        config,
    ):
        _print_interrupt(event)

    print("\n👤 Human approves the revised proposal.")
    final_state = None
    for event in graph.stream(Command(resume={"approved": True}), config):
        final_state = event

    state = graph.get_state(config).values
    print(f"\n✅ Final: {state['final']}")


if __name__ == "__main__":
    main()
