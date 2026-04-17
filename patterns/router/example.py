"""Runnable demo of the Router pattern.

Usage:
    python -m patterns.router.example
"""

from patterns.router.graph import build_graph

QUESTIONS = [
    "My React effect runs twice on mount — what's going on?",
    "Should I use a message bus or direct HTTP calls between my two new services?",
    "Can you review this Python function? `def f(xs): return [x for x in xs if x != None]`",
]


def main() -> None:
    graph = build_graph()
    for q in QUESTIONS:
        print(f"\n{'=' * 72}\nQ: {q}\n")
        result = graph.invoke(
            {"question": q, "route": None, "route_reason": None, "answer": None}
        )
        print(f"→ Routed to: {result['route']}  ({result['route_reason']})")
        print(f"\n{result['answer']}\n")


if __name__ == "__main__":
    main()
