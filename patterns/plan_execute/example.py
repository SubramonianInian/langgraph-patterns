"""Runnable demo of the Plan → Execute pattern.

Usage:
    python -m patterns.plan_execute.example
"""

from patterns.plan_execute.graph import build_graph


def main() -> None:
    graph = build_graph()
    result = graph.invoke(
        {
            "objective": (
                "Produce a one-page migration brief for moving a monolithic Node.js API "
                "to a modular service-oriented architecture on Azure."
            ),
            "plan": [],
            "current_step": 0,
            "step_outputs": [],
            "final": "",
        }
    )

    print("📋 Plan:")
    for i, step in enumerate(result["plan"], 1):
        print(f"  {i}. {step}")

    print(f"\n{'=' * 72}\nFinal brief:\n{'=' * 72}\n")
    print(result["final"])


if __name__ == "__main__":
    main()
