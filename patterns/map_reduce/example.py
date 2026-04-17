"""Runnable demo of the Map-Reduce pattern.

Reviews three short code snippets in parallel through a 'performance' lens,
then synthesizes consolidated findings.

Usage:
    python -m patterns.map_reduce.example
"""

from patterns.map_reduce.graph import build_graph


SNIPPETS = [
    """def total(items):
    result = 0
    for i in items:
        result = result + i
    return result""",
    """def dedup(items):
    out = []
    for i in items:
        if i not in out:
            out.append(i)
    return out""",
    """def load_users():
    users = []
    for id in user_ids:
        users.append(db.query(f"SELECT * FROM users WHERE id = {id}"))
    return users""",
]


def main() -> None:
    graph = build_graph()
    result = graph.invoke(
        {
            "theme": "performance (time complexity, N+1 queries, allocations)",
            "items": SNIPPETS,
            "findings": [],
            "synthesis": "",
        }
    )

    print("🔍 Per-snippet findings:")
    for i, f in enumerate(result["findings"], 1):
        print(f"\n[{i}] {f}")

    print(f"\n{'=' * 72}\nConsolidated synthesis:\n{'=' * 72}\n")
    print(result["synthesis"])


if __name__ == "__main__":
    main()
