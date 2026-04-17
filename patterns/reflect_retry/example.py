"""Runnable demo of the Reflect & Retry pattern.

Usage:
    python -m patterns.reflect_retry.example
"""

from patterns.reflect_retry.graph import build_graph


def main() -> None:
    graph = build_graph()
    result = graph.invoke(
        {
            "topic": "why RAG often fails in production",
            "criteria": (
                "- Must mention at least 3 distinct failure modes.\n"
                "- Must include one concrete mitigation per failure mode.\n"
                "- Must be under 200 words.\n"
                "- Must NOT use the phrase 'leverage' or 'seamless'."
            ),
            "draft": "",
            "feedback": "",
            "attempts": 0,
            "max_attempts": 3,
            "passed": False,
        }
    )

    print(f"\n✓ Passed: {result['passed']}  |  Attempts: {result['attempts']}")
    print(f"\n{'=' * 72}\nFinal draft:\n{'=' * 72}\n")
    print(result["draft"])
    if not result["passed"] and result["feedback"]:
        print(f"\n{'-' * 72}\nUnresolved feedback:\n{result['feedback']}")


if __name__ == "__main__":
    main()
