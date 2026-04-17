"""Runnable demo of the Memory pattern.

Simulates two sessions for the same user. Facts written in session 1 are
recalled in session 2 without repetition by the user.

Usage:
    python -m patterns.memory.example
"""

from patterns.memory.graph import build_graph
from patterns.memory.store import STORE


def _turn(graph, user_id: str, user_message: str) -> str:
    result = graph.invoke(
        {
            "user_id": user_id,
            "messages": [{"role": "user", "content": user_message}],
            "recalled": [],
            "response": "",
        }
    )
    return result["response"]


def main() -> None:
    graph = build_graph()
    user = "user-42"

    print("── Session 1 ──")
    q1 = "I'm allergic to shellfish, and I'm planning a trip to Lisbon next month."
    print(f"user: {q1}")
    print(f"bot:  {_turn(graph, user, q1)}")

    print(f"\nLong-term store now holds: {STORE.read(user, 'Lisbon shellfish')}")

    print("\n── Session 2 (later) ──")
    q2 = "Recommend a restaurant for my trip."
    print(f"user: {q2}")
    print(f"bot:  {_turn(graph, user, q2)}")


if __name__ == "__main__":
    main()
