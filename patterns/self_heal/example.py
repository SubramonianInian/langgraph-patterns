"""Runnable demo of the Self-Heal pattern.

Both tools are deliberately flaky (90% / 60% failure rates). Running
multiple times shows the fallback chain exercising each tier.

Usage:
    python -m patterns.self_heal.example
"""

from patterns.self_heal.graph import build_graph

LEVEL_NAMES = {0: "primary", 1: "secondary", 2: "cache", 3: "apology"}


def _run(query: str) -> None:
    graph = build_graph()
    result = graph.invoke(
        {
            "query": query,
            "attempts": [],
            "degradation_level": 0,
            "response": "",
        }
    )
    print(f"\nQ: {query}")
    print(f"→ Served from: {LEVEL_NAMES[result['degradation_level']]}")
    print(f"→ Path: {' → '.join(result['attempts'])}")
    print(f"→ Response:\n{result['response']}")


def main() -> None:
    for _ in range(3):
        _run("what is RAG?")


if __name__ == "__main__":
    main()
